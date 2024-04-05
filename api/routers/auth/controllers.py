import os
from datetime import datetime, timedelta, timezone
from enum import Enum

from jose import jwt
from sqlalchemy.orm import Session

from api.routers.users.controllers import get_user_by_username

SECRET_KEY = os.environ.get("SECRET_KEY", "")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "")
ACCESS_TOKEN_EXPIRES_MINUTES = 30

class Scopes(str, Enum):
        read_me = "users:me"
        read_users = "users:read"
        write_users = "users:write"


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(username, db)
    if not user:
        return False
    if not user.validate_password(password):
        return False
    return user


def create_token(data: dict, expires_in: timedelta | None = None, scopes: list[str] = []):
    to_encode = data.copy()
    if not expires_in:
        expires = datetime.now(timezone.utc) + \
            timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    else:
        expires = datetime.now(timezone.utc) + expires_in
    to_encode.update({"exp": expires})
    if scopes:
        to_encode.update({"scopes": scopes})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, JWT_ALGORITHM)
    return encoded_jwt
