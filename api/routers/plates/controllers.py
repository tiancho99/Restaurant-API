from sqlalchemy.exc import IntegrityError
from typing import Annotated

from fastapi import Depends, Body, Path
from sqlalchemy import select
from . models import PlatesDB, PlateIn
from api.dependencies import get_db
from sqlalchemy.orm import Session
from api.exceptions import integirty_exception, not_found_exception


def get_plates(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(PlatesDB)).all()


def create_plate(plate: Annotated[PlateIn, Body()], db: Annotated[Session, Depends(get_db)]):
    try:
        new_plate = PlatesDB(**plate.model_dump())
        db.add(new_plate)
        db.commit()
        db.refresh(new_plate)
    except IntegrityError:
        raise integirty_exception(field="name")
    return new_plate


def update_plate(
    plate_id: Annotated[int, Path],
    plate_data: Annotated[PlateIn, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    plate = db.get(PlatesDB, plate_id)
    if not plate:
        raise not_found_exception
    plate.update_plate(**plate_data.model_dump())
    db.commit()
    db.refresh(plate)
    return plate


def delete_plate(plate_id: Annotated[int, Path()], db: Annotated[Session, Depends(get_db)]):
    plate = db.get(PlatesDB, plate_id)
    if not plate:
        raise not_found_exception
    db.delete(plate)
    db.commit()
    return True

