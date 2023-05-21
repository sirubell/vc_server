from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.orm import relationship

from vc_server.database.database import Base
from vc_server.config import need_email_validation


class User(Base):
    __tablename__ = "users"

    user_name = Column(String, primary_key=True, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # TODO: for testing, turn off email validation
    is_active = Column(Boolean, default=not need_email_validation)
    is_admin = Column(Boolean, default=False)
    email_validation_code = Column(String)

    user_shares = relationship("UserShare", back_populates="user", cascade='all, delete')


class Door(Base):
    __tablename__ = "doors"

    door_name = Column(String, primary_key=True, unique=True, index=True)
    share = Column(String, unique=True)
    secret = Column(String, unique=True)

    door_keys = relationship("UserShare", back_populates="door", cascade='all, delete')


class UserShare(Base):
    __tablename__ = "shares"

    user_name = Column(String, ForeignKey("users.user_name"))
    door_name = Column(String, ForeignKey("doors.door_name"))
    share = Column(String, primary_key=True, unique=True, index=True)
    is_validated = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)

    user = relationship("User", back_populates="user_shares")
    door = relationship("Door", back_populates="door_keys")
