from sqlalchemy.orm import Session
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from vc_server.dependencies import get_db, get_current_active_user
from vc_server.database import crud
from vc_server.config import need_email_validation
from vc_server.utils.email import generate_validation_code, send_email
from vc_server import schemas

router = APIRouter(prefix="/users", tags=["users"])


async def _create_user(user: schemas.UserCreate, db: Session, is_admin=False):
    exception = HTTPException(
        status_code=400, detail="The name or email is already in use."
    )

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise exception
    db_user = crud.get_user_by_user_name(db, user_name=user.user_name)
    if db_user:
        raise exception

    if need_email_validation:
        code = generate_validation_code()
        await send_email(user.email, code)

    crud.create_user(db=db, user=user, code=code, is_admin=is_admin)


@router.post("/createUser", status_code=status.HTTP_204_NO_CONTENT)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    await _create_user(user, db, is_admin=False)


@router.get("/validateEmail", status_code=status.HTTP_204_NO_CONTENT)
def validate_email(code: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_validation_code(db, code)
    if db_user is None:
        raise HTTPException(
            status_code=400,
            detail="Not a valid credential code.",
        )
    db_user.is_active = True
    db.commit()


@router.get("/getMyKeys", response_model=List[schemas.UserShareData])
def get_my_keys(
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_shares = crud.get_not_blacklisted_and_validated_user_shares_by_user_name(
        db,
        user.user_name,
    )
    return user_shares


@router.post("/requestKey", status_code=status.HTTP_204_NO_CONTENT)
def request_key(
    door: schemas.DoorName,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_door = crud.get_door_by_door_name(db, door.door_name)
    if db_door is None:
        raise HTTPException(status_code=400, detail="Door is not exists.")

    user_share = crud.get_not_blacklisted_user_shares_by_user_and_door_name(
        db, current_user.user_name, door.door_name
    )
    if user_share is not None:
        raise HTTPException(status_code=400, detail="You already had the key.")

    crud.create_user_share(db, current_user, db_door)


@router.put("/requestUpdateKey", status_code=status.HTTP_204_NO_CONTENT)
def request_update_key(
    share: schemas.Share,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_user_share = crud.update_user_share(db, share)
    if db_user_share is None:
        raise HTTPException(status_code=404)


@router.delete("/deleteUser", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    crud.delete_user(db, user.user_name)


@router.delete("/deleteKey", status_code=status.HTTP_204_NO_CONTENT)
def delete_key(
    door: schemas.Share,
    user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    crud.delete_user_share(db, door.share)
