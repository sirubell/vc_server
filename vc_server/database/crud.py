import base64

from sqlalchemy.orm import Session

from vc_server import schemas, vc_share
from vc_server.database import models
from vc_server.utils.password import password_hash
from vc_server.config import need_email_validation


def get_user_shares(
    db: Session,
    offset: int = 0,
    limit: int = 100,
    user_name: str | None = None,
    door_name: str | None = None,
    is_validated: bool | None = None,
    is_blacklisted: bool | None = None,
) -> list[models.UserShare]:
    query = db.query(models.UserShare)
    if user_name:
        query = query.filter(models.UserShare.user_name == user_name)
    if door_name:
        query = query.filter(models.UserShare.door_name == door_name)
    if is_validated:
        query = query.filter(models.UserShare.is_validated.is_(is_validated))
    if is_blacklisted:
        query = query.filter(
            models.UserShare.is_blacklisted.is_(is_blacklisted))
    return query.offset(offset).limit(limit).all()


def get_user_share_by_share(db: Session, share: str) -> models.UserShare | None:
    return db.query(models.UserShare).filter(models.UserShare.share == share).first()


def get_not_blacklisted_user_shares_by_user_and_door_name(
    db: Session, user_name: str, door_name: str
) -> models.UserShare | None:
    return (
        db.query(models.UserShare)
        .filter(models.UserShare.user_name == user_name)
        .filter(models.UserShare.door_name == door_name)
        .filter(models.UserShare.is_blacklisted.is_(False))
        .first()
    )


def get_not_blacklisted_and_validated_user_shares_by_user_name(
    db: Session, user_name: str
) -> list[models.UserShare]:
    return (
        db.query(models.UserShare)
        .filter(models.UserShare.user_name == user_name)
        .filter(models.UserShare.is_blacklisted.is_(False))
        .filter(models.UserShare.is_validated.is_(True))
        .all()
    )


def get_user_by_user_name(db: Session, user_name: str) -> models.User | None:
    return db.query(models.User).filter(models.User.user_name == user_name).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def delete_user(db: Session, user_name: str) -> None:
    db_user = db.query(models.User).filter(models.User.user_name == user_name).first()
    if db_user:
        db.delete(db_user)
        db.commit()


def get_users(db: Session, offset: int = 0, limit: int = 100) -> list[models.User]:
    return db.query(models.User).offset(offset).limit(limit).all()


def create_user(
    db: Session,
    user: schemas.UserCreate,
    code: str | None,
    is_admin: bool = False,
) -> models.User:
    hashed_password = password_hash(user.password)
    db_user = models.User(
        user_name=user.user_name,
        email=user.email,
        hashed_password=hashed_password,
        email_validation_code=code if code is not None else "",
        is_active=not need_email_validation,
        is_admin=is_admin,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_validation_code(db: Session, code: str) -> models.User | None:
    return (
        db.query(models.User).filter(
            models.User.email_validation_code == code).first()
    )


def get_door_by_door_name(db: Session, door_name: str) -> models.Door | None:
    return db.query(models.Door).filter(models.Door.door_name == door_name).first()


def get_door_by_secret(db: Session, secret: str) -> models.Door | None:
    return db.query(models.Door).filter(models.Door.secret == secret).first()


def get_door_by_user_share(db: Session, user_share: str) -> models.Door | None:
    db_user_share = (
        db.query(models.UserShare).filter(
            models.UserShare.share == user_share).first()
    )
    if db_user_share is None:
        return None
    return db_user_share.door


def get_doors(db: Session, offset: int = 0, limit: int = 100) -> list[models.Door]:
    return db.query(models.Door).offset(offset).limit(limit).all()


def delete_door(db: Session, secret: str) -> None:
    db_door = db.query(models.Door).filter(
        models.Door.secret == secret).first()
    if db_door:
        db.delete(db_door)
        db.commit()


def delete_user_share(db: Session, share: str) -> None:
    db_user_share = db.query(models.UserShare).filter(
        models.UserShare.share == share)
    if db_user_share:
        db.delete(db_user_share)
        db.commit()


def create_door(db: Session, door_name: str) -> models.Door:
    secret = vc_share.create_secret()
    door_share = vc_share.create_door_share(door_name)

    db_door = models.Door(
        door_name=door_name,
        share=base64.b64encode(door_share).decode(),
        secret=base64.b64encode(secret).decode(),
    )

    db.add(db_door)
    db.commit()
    db.refresh(db_door)
    return db_door


def create_user_share(
    db: Session, user: schemas.User, door: schemas.DoorData
) -> models.UserShare:
    secret = base64.b64decode(door.secret)
    door_share = base64.b64decode(door.share)
    user_share = vc_share.create_user_share(user.user_name, secret, door_share)

    db_user_share = models.UserShare(
        user_name=user.user_name,
        door_name=door.door_name,
        share=base64.b64encode(user_share).decode(),
    )

    db.add(db_user_share)
    db.commit()
    db.refresh(db_user_share)
    return db_user_share


def update_user_share(db: Session, share: schemas.Share) -> schemas.UserShare | None:
    db_user_share = get_user_share_by_share(db, share.share)
    if db_user_share is None:
        return None
    db_user_share.is_blacklisted = True
    db.commit()

    new_user_share = create_user_share(
        db, db_user_share.user, db_user_share.door)
    new_user_share.is_validated = True
    db.commit()
    db.refresh(new_user_share)
    return new_user_share
