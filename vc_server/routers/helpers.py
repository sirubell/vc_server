from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import List

from fastapi import APIRouter, Depends, status

from vc_server.dependencies import get_db, get_current_user
from vc_server.database import database, models, crud
from vc_server.routers.users import _create_user
from vc_server import schemas

router = APIRouter(prefix="/helpers", tags=["helpers"])


@router.get("/clearDatabase", status_code=status.HTTP_204_NO_CONTENT)
def clear_database(db: Session = Depends(get_db)):
    models.Base.metadata.drop_all(bind=database.engine)
    models.Base.metadata.create_all(bind=database.engine)

    user_admin = crud.create_user(db, schemas.UserCreate(user_name="admin", email=EmailStr("sirius65535@gmail.com"), password="0000"), None, True)
    user1 = crud.create_user(db, schemas.UserCreate(user_name="王景誠", email=EmailStr("s410985051@gm.ntpu.edu.tw"), password="123"), None, False)
    user2 = crud.create_user(db, schemas.UserCreate(user_name="陳麒升", email=EmailStr("s410985034@gm.ntpu.edu.tw"), password="123"), None, False)
    user3 = crud.create_user(db, schemas.UserCreate(user_name="鐘皓暄", email=EmailStr("stu9932142@gmail.com"), password="123"), None, False)
    user4 = crud.create_user(db, schemas.UserCreate(user_name="盧冠翰", email=EmailStr("s410985067@gm.ntpu.edu.tw"), password="123"), None, False)
    user5 = crud.create_user(db, schemas.UserCreate(user_name="黃冠穎", email=EmailStr("s410987032@gm.ntpu.edu.tw"), password="123"), None, False)

    door1 = crud.create_door(db, door_name="電資院501實驗室")
    door2 = crud.create_door(db, door_name="電資院502實驗室")
    door3 = crud.create_door(db, door_name="電資院503實驗室")
    door4 = crud.create_door(db, door_name="電資院504實驗室")
    door5 = crud.create_door(db, door_name="電資院505實驗室")
    door6 = crud.create_door(db, door_name="電資院大門")

    crud.create_user_share(db, user_admin, door1, True)
    crud.create_user_share(db, user_admin, door2, True)
    crud.create_user_share(db, user_admin, door3, True)
    crud.create_user_share(db, user_admin, door4, True)
    crud.create_user_share(db, user_admin, door5, True)
    crud.create_user_share(db, user_admin, door6, True)

    crud.create_user_share(db, user1, door6, True)
    crud.create_user_share(db, user2, door6, True)
    crud.create_user_share(db, user3, door6, True)
    crud.create_user_share(db, user4, door6, True)
    crud.create_user_share(db, user5, door6, True)

    crud.create_user_share(db, user1, door1, True)
    crud.create_user_share(db, user2, door2, True)
    crud.create_user_share(db, user3, door3, True)
    crud.create_user_share(db, user4, door4, True)
    crud.create_user_share(db, user5, door5, True)

    crud.create_user_share(db, user1, door5, False)
    crud.create_user_share(db, user2, door5, False)
    crud.create_user_share(db, user3, door5, False)
    crud.create_user_share(db, user4, door5, False)

    crud.create_user_share(db, user1, door2, False)
    crud.create_user_share(db, user2, door4, False)
    crud.create_user_share(db, user3, door1, False)
    crud.create_user_share(db, user4, door3, False)
    crud.create_user_share(db, user5, door1, False)


@router.get("/getAllUsers", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@router.get("/getAllDoors", response_model=List[schemas.Door])
def get_doors(db: Session = Depends(get_db)):
    return crud.get_doors(db)


@router.get("/getAllUserShares", response_model=List[schemas.UserShare])
def get_all_user_shares(db: Session = Depends(get_db)):
    """
    helper function
    得到所有使用者Share
    """
    return crud.get_user_shares(db)


@router.get("/getMe", response_model=schemas.User)
def get_me(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return current_user


@router.get("/getMyKeys", response_model=List[schemas.UserShare])
def get_current_key(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return current_user.user_shares


@router.post("/createAdmin", status_code=status.HTTP_204_NO_CONTENT)
async def create_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    await _create_user(user, db, is_admin=True)
