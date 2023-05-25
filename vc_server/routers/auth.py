from sqlalchemy.orm import Session
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from vc_server.dependencies import get_db
from vc_server.utils.token import create_access_token
from vc_server.utils.password import verify_password
from vc_server.database import crud
from vc_server import schemas

router = APIRouter(tags=["users", "admin"])


def authenticate_user(db: Session, uesrname: str, password: str):
    user = crud.get_user_by_email(db, uesrname)
    if not user:
        user = crud.get_user_by_user_name(db, uesrname)
        if not user:
            return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.user_name})
    return {"access_token": access_token, "token_type": "bearer"}
