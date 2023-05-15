from pydantic import BaseModel, EmailStr


class UserShare(BaseModel):
    doorName: str
    share: str
    owner_id = int
    validated = bool
    updated = bool

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    userName: str


class User(UserBase):
    id: int
    is_active: bool
    user_shares: list[UserShare] = []

    class Config:
        orm_mode = True


class DoorCreate(BaseModel):
    doorName: str


class DoorSecret(DoorCreate):
    secret: str


class Door(DoorSecret):
    doorShare: str

    class Config:
        orm_mode = True
