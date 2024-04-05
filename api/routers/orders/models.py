from __future__ import annotations
from api.dependencies import get_db
from api.routers.plates.models import PlateOut, PlatesDB

from datetime import datetime
from typing import Dict, List

from click import DateTime
from pydantic import BaseModel, Field
from sqlalchemy import (Boolean, DateTime, Float, ForeignKey, Integer,
                        event)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.sql_app import Base


class OrderDetailBase(BaseModel):
    quantity: int = Field(default=1, gt=0)


class OrderDetailIn(OrderDetailBase):
    plate_id: int


class OrderDetailOut(OrderDetailBase):
    plate_id: int
    subtotal: float
    plate: PlateOut

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    is_paid: bool = False


class OrderIn(OrderBase):
    order_detail: Dict[int, int] = Field(
        description="A dictionary where keys are plate IDs and values are plate quantities.",
        examples=[{1: 2, 2: 1}],
        default={1: 2},
    )


class OrderOut(OrderBase):
    id: int
    date: datetime
    total: float
    order_detail: list[OrderDetailOut]


class OrderInDB(OrderBase):
    total: float = 0


class OrderDetail(Base):
    __tablename__ = 'order_details'
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('orders.id'), primary_key=True)
    plate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('plates.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)
    subtotal: Mapped[float] = mapped_column(Float)
    order: Mapped["OrdersDB"] = relationship(
        back_populates='order_detail')
    plate: Mapped["PlatesDB"] = relationship()

    def __init__(self, quantity: int, order: OrdersDB, plate: PlatesDB):
        self.quantity = quantity
        self.order = order
        self.plate = plate
        self.subtotal = plate.price * quantity

    def update_detail(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.subtotal = self.quantity * self.plate.price

class OrdersDB(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    total: Mapped[float] = mapped_column(Float)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_paid: Mapped[bool] = mapped_column(Boolean)
    order_detail: Mapped[List["OrderDetail"]
                         ] = relationship(back_populates="order", cascade="all, delete-orphan")

    def update_order(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@event.listens_for(OrderDetail, 'before_insert')
def receive_delete_insert(mapper, connection, target):
    order = target.order
    order.total += target.subtotal
    connection.execute(
        OrdersDB.__table__.update()
        .where(OrdersDB.id == order.id)
        .values(total=order.total)
    )

@event.listens_for(OrderDetail, 'before_delete')
def receive_before_delete(mapper, connection, target):
    order = target.order
    order.total -= target.subtotal
    connection.execute(
        OrdersDB.__table__.update()
        .where(OrdersDB.id == order.id)
        .values(total=order.total)
    )


@event.listens_for(OrderDetail, 'before_update')
def receive_after_update(mapper, connection, target):
    order = target.order
    order.total = sum([detail.subtotal for detail in order.order_detail])
    connection.execute(
        OrdersDB.__table__.update()
        .where(OrdersDB.id == order.id)
        .values(total=order.total)
    )