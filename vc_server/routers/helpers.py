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


@router.get("/getAllUsers", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@router.get("/getAllDoors", response_model=List[schemas.Door])
def get_doors(db: Session = Depends(get_db)):
    return crud.get_doors(db)


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


@router.get("/getAllUserShares", response_model=List[schemas.UserShare])
def get_all_user_shares(db: Session = Depends(get_db)):
    """
    helper function
    得到所有使用者Share
    """
    return crud.get_user_shares(db)


@router.post("/createAdmin", status_code=status.HTTP_204_NO_CONTENT)
async def create_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    await _create_user(user, db, is_admin=True)
