from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from vc_server.dependencies import get_db
from vc_server.database import crud
from vc_server import schemas

router = APIRouter(prefix="/doors", tags=["doors"])


@router.post("/createDoor", response_model=schemas.DoorData)
def create_door(door: schemas.DoorName, db: Session = Depends(get_db)):
    exception = HTTPException(
        status_code=400,
        detail="The name is already in use.",
    )
    db_door = crud.get_door_by_door_name(db, door.door_name)
    if db_door:
        raise exception

    return crud.create_door(db, door.door_name)


@router.post("/updateDoor", response_model=schemas.DoorUpdate)
def update_door(door: schemas.DoorSecret, db: Session = Depends(get_db)):
    db_door = crud.get_door_by_secret(db, door.secret)
    if db_door is None:
        raise HTTPException(status_code=404)

    blacklist = [
        user_share.share
        for user_share in db_door.door_keys
        if user_share.is_blacklisted
    ]

    return schemas.DoorUpdate(
        door_name=db_door.door_name,
        share=db_door.share,
        secret=db_door.secret,
        is_blacklisted=blacklist,
    )


@router.delete("/deleteDoor", status_code=status.HTTP_204_NO_CONTENT)
def delete_door(door: schemas.DoorSecret, db: Session = Depends(get_db)):
    crud.delete_door(db, door.secret)
