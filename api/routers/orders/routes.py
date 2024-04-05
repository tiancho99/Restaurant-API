from typing import Annotated
from . import orders_router
from . import controllers
from .models import OrderDetail, OrderDetailOut, OrderOut, OrdersDB
from fastapi import Depends

from api.routers import orders


@orders_router.get("/", response_model=list[OrderOut])
async def get_orders(orders: Annotated[list[OrdersDB], Depends(controllers.get_orders)]):
    return orders


@orders_router.get("/{order_id}", response_model=OrderOut)
async def get_order(order: Annotated[OrdersDB, Depends(controllers.get_order)]):
    return order


@orders_router.post("/", response_model=OrderOut)
async def create_order(order: Annotated[OrdersDB, Depends(controllers.create_order)]):
    return order


@orders_router.put("/{order_id}", response_model=OrderOut)
async def update_order(updated_order: Annotated[OrdersDB, Depends(controllers.update_order)]):
    return updated_order


@orders_router.delete("/{order_id}")
async def delete_order(is_deleted: Annotated[bool, Depends(controllers.delete_order)]):
    return is_deleted


@orders_router.get("/{order_id}/details", response_model=list[OrderDetailOut])
async def get_order_details(order_details: Annotated[OrderDetail, Depends(controllers.get_order_details)]):
    return order_details


@orders_router.get("/{order_id}/details/{plate_id}", response_model=OrderDetailOut)
async def get_order_detail(order_detail: Annotated[OrderDetail, Depends(controllers.get_order_detail)]):
    return order_detail


@orders_router.post("/{order_id}/details", response_model=OrderDetailOut)
async def create_order_detail(order_detail: Annotated[OrderDetail, Depends(controllers.create_order_detail)]):
    return order_detail


@orders_router.put("/{order_id}/details/{plate_id}", response_model=OrderDetailOut)
async def update_order_detail(order_detail: Annotated[OrderDetail, Depends(controllers.update_oder_detail)]):
    return order_detail


@orders_router.delete("/{order_id}/details/{plate_id}")
async def delete_order_detail(order_detail: Annotated[bool, Depends(controllers.delete_order_detail)]) -> bool:
    return order_detail
