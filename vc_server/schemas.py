from pydantic import BaseModel, EmailStr


class Share(BaseModel):
    share: str


class UserShareName(BaseModel):
    user_name: str
    door_name: str


class UserShareData(UserShareName, Share):
    class Config:
        orm_mode = True


class UserShare(UserShareData):
    is_validated: bool
    is_blacklisted: bool

    class Config:
        orm_mode = True


class UserName(BaseModel):
    user_name: str


class UserEmail(BaseModel):
    email: EmailStr


class UserPassword(BaseModel):
    password: str


class UserCreate(UserName, UserEmail, UserPassword):
    pass


class UserData(UserName, UserEmail):
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class User(UserData):
    user_shares: list[UserShare] = []

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    shares: list[UserShare] = []

    class Config:
        orm_mode = True


class DoorName(BaseModel):
    door_name: str


class DoorSecret(BaseModel):
    secret: str


class DoorData(DoorName, Share, DoorSecret):
    class Config:
        orm_mode = True


class Door(DoorData):
    door_keys: list[UserShare] = []

    class Config:
        orm_mode = True


class DoorUpdate(DoorData, Share):
    is_blacklisted: list[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_name: str | None = None
