from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

authentication_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not enough permissions",
)

inactivity_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Inactive user"
)


def not_found_exception(resource=""):
    return HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found",
        headers={"WWW-Authenticate": "Bearer"}
    )

    return HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail="Resource you are trying to access was not found",
        headers={"WWW-Authenticate": "Bearer"}
    )


def integirty_exception(field: str):
    e = HTTPException(
        status.HTTP_409_CONFLICT,
        detail=f"{field} already exists.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return e
