import os
from typing import Annotated
from anyio import Path

from fastapi import Body, Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.exceptions import *
from api.routers.auth.models import TokenData

from .models import *

SECRET_KEY = os.environ.get("SECRET_KEY", "")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "users:me": "Read current user information",
        "users:read": "Perform users read operations",
        "users:write": "Perform users writting operations",
    }
)


def get_user_by_username(
        username: str,
        db: Session
):
    user = db.scalars(select(UsersDB).where(
        UsersDB.username == username)).first()
    return user


def _get_payload(access_token: str):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, JWT_ALGORITHM)
        return payload
    except JWTError:
        raise credentials_exception


def _validate_scopes(security_scopes: SecurityScopes, token_scopes: list[str]):
    if security_scopes.scopes:
        authenticate_value = f"Bearer scope='{security_scopes.scope_str}'"
    else:
        authenticate_value = "Bearer"
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            authentication_exception.headers = {
                "WWW-Authenticate": authenticate_value}
            raise authentication_exception
    return True


def create_user(
    security_scopes: SecurityScopes,
    user: Annotated[UserIn, Body()],
    db: Annotated[Session, Depends(get_db)],
    access_token: Annotated[str, Depends(oauth2_scheme)]
):
    payload = _get_payload(access_token)
    token_scopes = payload.get("scopes", [])
    if _validate_scopes(security_scopes, token_scopes):
        pass
    try:
        db_user_model = UserInDB.create(user)
        db_user = UsersDB(**db_user_model.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        email_exists = "users.email" in e.args[0]
        field = "Email" if email_exists else "Username"
        raise integirty_exception(field)
    return db_user


def get_users(
    security_scopes: SecurityScopes,
    db: Annotated[Session, Depends(get_db)],
    access_token: Annotated[str, Depends(oauth2_scheme)]
):
    payload = _get_payload(access_token)
    token_scopes = payload.get("scopes", [])
    if _validate_scopes(security_scopes, token_scopes):
        pass
    users = db.scalars(select(UsersDB)).all()
    return users


def get_user(
    security_scopes: SecurityScopes,
    username: Annotated[str, Path()],
    db: Annotated[Session, Depends(get_db)],
    access_token: Annotated[str, Depends(oauth2_scheme)]
):
    payload = _get_payload(access_token)
    token_scopes = payload.get("scopes", [])
    if _validate_scopes(security_scopes, token_scopes):
        pass
    user = get_user_by_username(username, db)
    if not user:
        raise not_found_exception("user")
    return user


async def get_current_user(
    security_scopes: SecurityScopes,
    db: Annotated[Session, Depends(get_db)],
    access_token: Annotated[str, Depends(oauth2_scheme)]
):
    payload = _get_payload(access_token)
    token_scopes = payload.get("scopes", [])
    if _validate_scopes(security_scopes, token_scopes):
        pass
    username = payload.get("sub", "")
    if not username:
        raise credentials_exception
    token_scopes = payload.get("scopes", [])
    token_data = TokenData(scopes=token_scopes, username=username)
    user = get_user_by_username(token_data.username, db)
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UsersDB, Security(get_current_user, scopes=["users:me"])]
) -> UsersDB:
    if not current_user.active:
        raise inactivity_exception
    return current_user
