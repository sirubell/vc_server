from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from vc_server.config import secret, algorithm
from vc_server.database import crud, database
from vc_server import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_name=user_name)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_user_name(next(get_db()), user_name=token_data.user_name)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_admin(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
    if not current_user.is_admin:
        raise HTTPException(status_code=401, detail="Not an admin")
    return current_user
