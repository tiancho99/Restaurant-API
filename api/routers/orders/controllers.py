from ast import Or
from datetime import datetime
from typing import Annotated

from fastapi import Path, Body, Depends, HTTPException, status
from httpcore import AnyIOBackend
import orjson
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.dependencies import get_db
from api.exceptions import integirty_exception, not_found_exception

from .models import OrderDetail, OrderDetailBase, OrderDetailIn, OrderIn, OrderInDB, OrdersDB
from api.routers.plates.models import PlatesDB


def _get_order_detail(order, order_detail, db) -> list[OrderDetail]:
    plates_id = list(order_detail.keys())
    plates_quantity = list(order_detail.values())
    plates = db.execute(select(PlatesDB).where(
        PlatesDB.id.in_(plates_id))).scalars()
    detail_list: list[OrderDetail] = []
    for i, plate in enumerate(plates):
        if not plate:
            raise not_found_exception("Plate")
        detail_data = OrderDetailBase(quantity=plates_quantity[i])
        new_detail = OrderDetail(
            **detail_data.model_dump(), order=order, plate=plate)
        detail_list.append(new_detail)
    return detail_list


async def get_order_detail(
    order_id: Annotated[int, Path()],
    plate_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)]
):
    detail = db.get(OrderDetail, (order_id, plate_id))
    if not detail:
        raise not_found_exception()
    return detail


async def get_order_details(
    order_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)]
):
    order = db.get(OrdersDB, order_id)
    if not order:
        raise not_found_exception()
    return order.order_detail


async def create_order_detail(
    order_id: Annotated[int, Path()],
    order_detail_body: Annotated[OrderDetailIn, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    order = db.get(OrdersDB, order_id)
    if not order:
        raise not_found_exception("Order")
    plate = db.get(PlatesDB, order_detail_body.plate_id)
    if not plate:
        raise not_found_exception("Plate")
    try:
        quantity = order_detail_body.quantity
        order_detail_data = OrderDetailBase(quantity=quantity)
        new_order_detail = OrderDetail(
            **order_detail_data.model_dump(), plate=plate, order=order)
        db.add(new_order_detail)
        db.commit()
        db.refresh(new_order_detail)
    except IntegrityError:
        raise integirty_exception("plate")
    return new_order_detail


async def update_oder_detail(
    order_id: Annotated[int, Path()],
    plate_id: Annotated[int, Path()],
    order_detail_data: Annotated[OrderDetailBase, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        order_detail = db.get(OrderDetail, (order_id, plate_id))
        if not order_detail:
            raise not_found_exception()
        order_detail.update_detail(**order_detail_data.model_dump())
        db.commit()
        db.refresh(order_detail)
    except IntegrityError:
        raise integirty_exception("plate")
    return order_detail


async def delete_order_detail(
    order_id: Annotated[int, Path()],
    plate_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)]
):
    detail = db.get(OrderDetail, (order_id, plate_id))
    if not detail:
        raise not_found_exception()
    db.delete(detail)
    db.commit()
    return True


async def get_orders(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(OrdersDB)).all()


async def get_order(
    order_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)]
):
    order = db.get(OrdersDB, order_id)
    if not order:
        raise not_found_exception("Order")
    return order


async def create_order(
    order_data: Annotated[OrderIn, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        order_detail = order_data.order_detail
        order_in_db = OrderInDB(**order_data.model_dump())
        new_order = OrdersDB(**order_in_db.model_dump())
        detail_list = _get_order_detail(new_order, order_detail, db)
        db.add_all(detail_list)
        db.commit()
    except IntegrityError as e:
        raise integirty_exception(field="id")
    return new_order


async def update_order(
    order_id: Annotated[int, Path()],
    order_data: Annotated[OrderIn, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        order = db.get(OrdersDB, order_id)
        if not order:
            raise not_found_exception("Order")
        # TODO
        if not order_data.order_detail:
            order.update_order(is_paid=order_data.is_paid)
            db.commit()
            db.refresh(order)
            return order
        order_detail = order.order_detail.copy()

        db.commit()
        db.refresh(order)
    except IntegrityError as e:
        raise integirty_exception(field="id")
    return order


async def delete_order(
    order_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)]
):
    order = db.get(OrdersDB, order_id)
    if not order:
        raise not_found_exception("Order")
    db.delete(order)
    db.commit()
    return True