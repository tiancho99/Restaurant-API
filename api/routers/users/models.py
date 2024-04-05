from passlib.hash import bcrypt
from pydantic import BaseModel
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.sql_app import Base


class UserBase(BaseModel):
    username: str
    email: str
    active: bool


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    hashed_password: str

    @classmethod
    def create(cls, user_in: UserIn):
        hashed_password = bcrypt.hash(user_in.password)
        return cls(**user_in.model_dump(), hashed_password=hashed_password)

class UsersDB(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    active: Mapped[bool] = mapped_column(Boolean)
    hashed_password: Mapped[str] = mapped_column(String)

    def validate_password(self, password: str):
        return bcrypt.verify(password, self.hashed_password)

        

