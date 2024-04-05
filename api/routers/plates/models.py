from __future__ import annotations

from typing import List

from pydantic import BaseModel
from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.sql_app import Base


class PlateBase(BaseModel):
    name: str
    description: str
    price: float
    available: bool = True

    class Config:
        from_attributes = True


class PlateIn(PlateBase):
    pass


class PlateOut(PlateBase):
    id: int

    class Config:
        from_attributes = True


class PlatesDB(Base):
    __tablename__ = "plates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    available: Mapped[bool] = mapped_column(Boolean)
    order_detail: Mapped["OrderDetail"] = relationship(
        back_populates="plate", cascade="all, delete-orphan")
    # detail: Mapped[List["OrdersDB"]] = relationship(secondary="order_details")

    def update_plate(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

from api.routers.orders.models import OrderDetail