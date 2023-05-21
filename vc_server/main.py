from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import Response
from fastapi_login import LoginManager
from datetime import timedelta
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas
from .database import SessionLocal, engine
from .hashing import Hasher
from .config import conf


models.Base.metadata.create_all(bind=engine)

manager = LoginManager(conf["SECRET"], token_url="/login", use_cookie=True)


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@manager.user_loader()
def load_user(email: str):
    with SessionLocal() as db:
        user = crud.get_user_by_email(db, email)
        return user


@app.get("/clearDatabase", status_code=status.HTTP_204_NO_CONTENT)
def clear_database(db: Session = Depends(get_db)):
    """
    清空資料庫，是一個helper function
    """
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)


@app.get("/getUsers")
def get_users(db: Session = Depends(get_db)):
    """
    helper function
    得到所有使用者
    """
    return crud.get_users(db)


@app.get("/getDoors", response_model=List[schemas.Door])
def get_doors(db: Session = Depends(get_db)):
    """
    helper function
    得到所有門鎖
    """
    return crud.get_doors(db)


@app.get("/getMe", response_model=schemas.User)
def get_me(user: schemas.User = Depends(manager), db: Session = Depends(get_db)):
    """
    helper function
    得到自己（使用者）的資訊
    """
    return crud.get_user(db, user.id)


@app.get("/getMyKeys", response_model=List[schemas.UserShare])
def get_current_key(
    current_user: schemas.User = Depends(manager),
    db: Session = Depends(get_db),
):
    """helper function 回傳把使用者的所有share"""

    current_user = crud.get_user(db, current_user.id)
    return current_user.user_shares


@app.get("/getAllUserShares", response_model=List[schemas.UserShare])
def get_all_user_shares(db: Session = Depends(get_db)):
    """
    helper function
    得到所有使用者Share
    """
    return crud.get_user_shares(db)


@app.post("/createUser", response_model=schemas.UserData)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    exception = HTTPException(
        status_code=400, detail="The name or email is already in use."
    )

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise exception
    db_user = crud.get_user_by_username(db, username=user.userName)
    if db_user:
        raise exception

    return await crud.create_user(db=db, user=user)


@app.get("/validateEmail", status_code=status.HTTP_204_NO_CONTENT)
def validate_email(code: str, db: Session = Depends(get_db)):
    db_user = crud.validate_email(db, code)
    if not db_user:
        raise HTTPException(status_code=400, detail="Not a valid credential code.")
    db_user.is_active = True
    db.commit()


@app.delete("/deleteUser", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user: schemas.User = Depends(manager),
    db: Session = Depends(get_db),
):
    crud.delete_user(db, user.id)


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    exception = HTTPException(
        status_code=400, detail="Email or password is not correct."
    )
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user:
        raise exception
    if not Hasher.verify_password(user.password, db_user.password):
        raise exception
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Not active yet.")

    token = manager.create_access_token(
        data=dict(sub=user.email), expires=timedelta(days=1)
    )

    response = Response(None)
    manager.set_cookie(response, token)

    return response


@app.post("/requestKey", status_code=status.HTTP_204_NO_CONTENT)
def request_key(
    door: schemas.DoorName,
    user: schemas.User = Depends(manager),
    db: Session = Depends(get_db),
):
    current_user = crud.get_user_by_email(db, user.email)
    db_door = crud.get_door_by_doorname(db, door.doorName)
    if not db_door:
        raise HTTPException(status_code=400, detail="Object is not exists.")
    for user_share in current_user.user_shares:
        if user_share.doorName == db_door.doorName:
            raise HTTPException(status_code=400, detail="Already applied.")

    crud.create_user_share(db, current_user, db_door)


@app.delete("/deleteKey", status_code=status.HTTP_204_NO_CONTENT)
def delete_key(
    door: schemas.DoorName,
    user: schemas.User = Depends(manager),
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, user.id)
    # TODO

    pass


@app.get("/userUpdate", response_model=schemas.UserUpdate)
def user_update(user=Depends(manager), db: Session = Depends(get_db)):
    response = schemas.UserUpdate()
    shares = crud.get_not_yet_update_shares(db, user.id)

    for share in shares:
        response.newShares.append(share)

    crud.update_shares(db, user.id)

    return response


@app.post("/createDoor", response_model=schemas.Door)
def create_door(door: schemas.DoorName, db: Session = Depends(get_db)):
    exception = HTTPException(status_code=400, detail="The name is already in use.")
    db_door = crud.get_door_by_doorname(db, door.doorName)
    if db_door:
        raise exception

    return crud.create_door(db, door.doorName)


@app.post("/updateDoor", response_model=schemas.Door)
def update_door(door: schemas.DoorSecret, db: Session = Depends(get_db)):
    return crud.get_door_by_secret(db, door.secret)


@app.delete("/deleteDoor", status_code=status.HTTP_204_NO_CONTENT)
def delete_door(door: schemas.DoorSecret, db: Session = Depends(get_db)):
    crud.delete_door(db, door)
