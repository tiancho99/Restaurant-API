from fastapi import FastAPI

from api.sql_app import Base, engine

from .routers.auth import auth_router
from .routers.users import users_router
from .routers.plates import plates_router
from .routers.orders import orders_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Authorization"])
app.include_router(plates_router, prefix="/plates", tags=["Plates"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])

app.title = "Restaurant API"
