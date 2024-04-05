from typing import Annotated
from fastapi import Depends
from . import plates_router
from . import controllers
from . models import PlatesDB, PlateOut


@plates_router.get("/", response_model=list[PlateOut])
def get_plates(plates: Annotated[PlatesDB, Depends(controllers.get_plates)]):
    return plates


@plates_router.post("/", response_model=PlateOut)
def create_plate(plate: Annotated[PlatesDB, Depends(controllers.create_plate)]):
    return plate


@plates_router.get("/{plate_id}")
def get_plate():
    pass


@plates_router.put("/{plate_id}", response_model=PlateOut)
def update_plate(plate: Annotated[PlatesDB, Depends(controllers.update_plate)]):
    return plate


@plates_router.delete("/{plate_id}", description="Should be only use in case you want to delete all information about a plate, since it will delete not only the plate but all the related orders.")
def delete_plate(response: Annotated[bool, Depends(controllers.delete_plate)]):
    return response
