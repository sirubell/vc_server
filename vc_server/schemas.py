from pydantic import BaseModel, EmailStr


class UserShareBase(BaseModel):
    doorName: str
    share: str


class UserShare(UserShareBase):
    owner_id = int
    validated = bool
    updated = bool

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr


class UserLogin(UserBase):
    password: str


class UserData(UserBase):
    userName: str

    class Config:
        orm_mode = True


class UserCreate(UserLogin, UserData):
    pass


class User(UserData):
    id: int
    is_active: bool
    user_shares: list[UserShare] = []

    class Config:
        orm_mode = True


class DoorName(BaseModel):
    doorName: str


class DoorSecret(DoorName):
    secret: str


class Door(DoorSecret):
    doorShare: str

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    deleteDoors: list[DoorName] = []
    newShares: list[UserShareBase] = []
