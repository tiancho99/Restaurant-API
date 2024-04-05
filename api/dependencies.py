import os

from api.sql_app import SessionLocal

SECRET_KEY = os.environ.get("SECRET_KEY", "")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "")


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
