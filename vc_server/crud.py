from sqlalchemy.orm import Session

from . import models, schemas, share, email
from .hashing import Hasher
from .config import conf


import base64


def get_user_shares(db: Session):
    return db.query(models.UserShare).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.userName == username).first()


def delete_user(db: Session, id: int):
    db.query(models.User).filter(models.User.id == id).delete()
    db.query(models.UserShare).filter(models.UserShare.owner_id == id).delete()
    db.commit()


def get_not_yet_update_shares(db: Session, id: int):
    return (
        db.query(models.UserShare)
        .join(models.UserShare.owner)
        .filter(models.UserShare.owner_id == id)
        .filter(models.UserShare.updated.is_(False))
        .all()
    )


def update_shares(db: Session, id: int):
    db.query(models.UserShare).filter(models.UserShare.owner_id == id).filter(
        models.UserShare.updated.is_(False)
    ).update({"updated": True})
    db.commit()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


async def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = Hasher.get_password_hash(user.password)
    code = ""
    if conf["need_email_validation"]:
        code = email.generate_validation_code()
        await email.send_email(user.email, code)

    db_user = models.User(
        userName=user.userName,
        email=user.email,
        password=hashed_password,
        email_valid_code=code,
        is_active=not conf["need_email_validation"],
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def validate_email(db: Session, code: str):
    return db.query(models.User).filter(models.User.email_valid_code == code).first()


def get_door_by_doorname(db: Session, doorname: str):
    return db.query(models.Door).filter(models.Door.doorName == doorname).first()


def get_door_by_secret(db: Session, secret: str):
    return db.query(models.Door).filter(models.Door.secret == secret).first()


def get_doors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Door).offset(skip).limit(limit).all()


def delete_door(db: Session, door: schemas.DoorSecret):
    db.query(models.Door).filter(models.Door.secret == door.secret).delete()
    db.commit()
    # TODO don't delete user shares immediately
    db.query(models.UserShare).filter(
        models.UserShare.doorName == door.doorName
    ).delete()


def create_door(db: Session, door_name: str):
    secret = share.create_secret()
    door_share = share.create_door_share(door_name)

    db_door = models.Door(
        doorName=door_name,
        doorShare=base64.b64encode(door_share).decode(),
        secret=base64.b64encode(secret).decode(),
    )
    db.add(db_door)
    db.commit()
    db.refresh(db_door)
    return db_door


def create_user_share(db: Session, user: schemas.UserData, door: schemas.Door):
    secret = base64.b64decode(door.secret)
    door_share = base64.b64decode(door.doorShare)
    user_share = share.create_user_share(user.userName, secret, door_share)

    db_user_share = models.UserShare(
        doorName=door.doorName,
        share=base64.b64encode(user_share).decode(),
        owner_id=user.id,
    )
    db.add(db_user_share)
    db.commit()
    db.refresh(db_user_share)
    return db_user_share
