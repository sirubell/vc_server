from sqlalchemy.orm import Session

from . import models, schemas
from .hashing import Hasher

import random
import base64


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


def create_user(db: Session, user: schemas.UserCreate, code: str):
    hashed_password = Hasher.get_password_hash(user.password)
    db_user = models.User(
        userName=user.userName,
        email=user.email,
        password=hashed_password,
        email_valid_code=code,
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
    # TODO delete user shares later
    db.query(models.UserShare).filter(
        models.UserShare.doorName == door.doorName
    ).delete()


def create_door(db: Session, doorName: str):
    secret = random.randbytes(50)
    doorShare = bytearray(200)
    doorNameBytes = doorName.encode().ljust(50, b"\0")

    white = [0, 0, 1, 1]
    black = [0, 1, 1, 1]

    def calculate_halfbyte(color, lowerbit):
        shuffled = random.sample(black, len(black))
        tmp = 0
        tmp |= shuffled[0] << 0
        tmp |= shuffled[1] << 1
        tmp |= shuffled[2] << 2
        tmp |= shuffled[3] << 3

        return tmp << (0 if lowerbit else 4)

    """
    尋訪門的名字的每個bit，如果為1則為黑色，如果為0則為白色。
    依序把shuffled過的list填入door share裡。
    """
    for i in range(50):
        byte = doorNameBytes[i]
        for j in range(8):
            lowerbit = j % 2 == 0
            share_index = i * 4 + j // 2
            if (byte >> j) & 1:
                """black"""
                doorShare[share_index] |= calculate_halfbyte(black, lowerbit)
            else:
                """white"""
                doorShare[share_index] |= calculate_halfbyte(white, lowerbit)

    db_door = models.Door(
        doorName=doorName,
        doorShare=base64.b64encode(doorShare).decode(),
        secret=base64.b64encode(secret).decode(),
    )
    db.add(db_door)
    db.commit()
    db.refresh(db_door)
    return db_door


table = [
    [
        {
            # secret white, user white
            3: [5, 6, 9, 10],
            5: [3, 6, 9, 12],
            6: [3, 5, 10, 12],
            7: [3, 5, 6],
            9: [3, 5, 10, 12],
            10: [3, 6, 9, 12],
            11: [3, 9, 10],
            12: [5, 6, 9, 10],
            13: [5, 9, 12],
            14: [6, 10, 12],
        },
        {
            # secret white, user black
            3: [7, 11],
            5: [7, 13],
            6: [7, 14],
            7: [7],
            9: [11, 13],
            10: [11, 14],
            11: [11],
            12: [13, 14],
            13: [13],
            14: [14],
        },
    ],
    [
        {
            # secret black, user white
            3: [12],
            5: [10],
            6: [9],
            7: [9, 10, 12],
            9: [6],
            10: [5],
            11: [5, 6, 12],
            12: [3],
            13: [3, 6, 10],
            14: [3, 5, 9],
        },
        {
            # secret black, user black
            3: [13, 14],
            5: [11, 14],
            6: [11, 13],
            7: [11, 13, 14],
            9: [7, 14],
            10: [7, 13],
            11: [7, 13, 14],
            12: [7, 11],
            13: [7, 11, 14],
            14: [7, 11, 13],
        },
    ],
]


def create_user_share(db: Session, user: schemas.User, door: schemas.Door):
    user_name = user.userName.encode().ljust(50, b"\0")
    secret = base64.b64decode(door.secret)
    door_share = base64.b64decode(door.doorShare)
    user_share = bytearray(200)

    """
    尋訪所有secret bit，同時找到相對應的door bit還有使用者名稱bit(各有四個)
    """
    for i in range(50):
        secret_byte = secret[i]
        user_name_byte = user_name[i]
        for j in range(8):
            secret_color = (secret_byte >> j) & 1
            user_color = (user_name_byte >> j) & 1
            share_index = i * 4 + j // 2
            shift = 0 if j % 2 == 0 else 4
            door_share_4bit = (door_share[share_index] >> shift) & 0xF

            user_choices = table[secret_color][user_color][door_share_4bit]
            user_share_4bit = random.choice(user_choices)

            user_share[share_index] |= user_share_4bit << shift

    db_user_share = models.UserShare(
        doorName=door.doorName,
        share=base64.b64encode(user_share).decode(),
        owner_id=user.id,
    )
    db.add(db_user_share)
    db.commit()
    db.refresh(db_user_share)
    return db_user_share
