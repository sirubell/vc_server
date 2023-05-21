from sqlalchemy.orm import Session
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from vc_server.dependencies import get_db, get_admin
from vc_server.database import crud
from vc_server import schemas

router = APIRouter(prefix="/admin", tags=["admin"])


@router.put("/validateUserShare", status_code=status.HTTP_204_NO_CONTENT)
def validate_user_share(
    user_share: schemas.Share,
    admin: schemas.User = Depends(get_admin),
    db: Session = Depends(get_db),
):
    user_share = crud.get_user_share_by_share(db, user_share.share)
    if user_share is None:
        raise HTTPException(status_code=404)
    user_share.is_validated = True
    db.commit()


@router.put("/setBlacklistUserShare", status_code=status.HTTP_204_NO_CONTENT)
def set_blacklist(
    user_share: schemas.Share,
    admin: schemas.User = Depends(get_admin),
    db: Session = Depends(get_db),
):
    user_share = crud.get_user_share_by_share(db, user_share.share)
    if user_share is None:
        raise HTTPException(status_code=404)
    user_share.is_blacklisted = True
    db.commit()


@router.get("/getUsers", response_model=List[schemas.UserData])
def get_users(
    offset: int = 0,
    limit: int = 100,
    admin: schemas.User = Depends(get_admin),
    db: Session = Depends(get_db),
):
    return crud.get_users(db, offset, limit)


@router.get("/getDoors", response_model=List[schemas.DoorData])
def get_doors(
    offset: int = 0,
    limit: int = 100,
    admin: schemas.User = Depends(get_admin),
    db: Session = Depends(get_db),
):
    return crud.get_doors(db, offset, limit)


@router.get("/getUserShares", response_model=List[schemas.UserShare])
def get_user_shares(
    offset: int = 0,
    limit: int = 100,
    user_name: str | None = None,
    door_name: str | None = None,
    is_validated: bool | None = None,
    is_blacklisted: bool | None = None,
    admin: schemas.User = Depends(get_admin),
    db: Session = Depends(get_db),
):
    return crud.get_user_shares(
        db, offset, limit, user_name, door_name, is_validated, is_blacklisted
    )
