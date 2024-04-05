from typing import Annotated

from fastapi import Body, Depends, Path, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.dependencies import get_db

from . import controllers, users_router
from .models import *


@users_router.get("/", response_model=list[UserOut])
async def get_users(users: Annotated[UsersDB, Security(controllers.get_users, scopes=["users:read"])]):
    return users


@users_router.post("/", response_model=UserOut)
async def create_user(
    user: Annotated[UsersDB, Security(controllers.create_user, scopes=["users:write"])],
    
):
    return user


@users_router.get("/me", response_model=UserOut)
def get_me(
    current_user: Annotated[UsersDB, Depends(controllers.get_current_active_user)]
):
    return current_user


@users_router.get("/{username}", response_model=UserOut)
async def get_user(
    user: Annotated[UsersDB, Security(controllers.get_user, scopes=["users:read"])]
):
    return user
