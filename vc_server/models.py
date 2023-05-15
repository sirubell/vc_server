from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class UserShare(Base):
    __tablename__ = "shares"

    doorName = Column(String)
    share = Column(String, primary_key=True, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    validated = Column(Boolean, default=True)
    updated = Column(Boolean, default=False)

    owner = relationship("User", back_populates="user_shares")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    userName = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    email_valid_code = Column(String)

    user_shares = relationship("UserShare", back_populates="owner")


class Door(Base):
    __tablename__ = "doors"

    id = Column(Integer, primary_key=True, index=True)
    doorName = Column(String, unique=True, index=True)
    doorShare = Column(String)
    secret = Column(String)
