from datetime import timedelta
from enum import Enum
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.dependencies import get_db

from . import auth_router
from . import controllers as ctrls
from .models import *



@auth_router.post("/token")
async def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = ctrls.authenticate_user(
        db,
        form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = ctrls.create_token(
        data={"sub": form_data.username, "scopes": [ctrls.Scopes.read_users,
                                                    ctrls.Scopes.read_me]}
    )

    return Token(access_token=access_token, token_type="bearer")
