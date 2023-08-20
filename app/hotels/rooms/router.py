from datetime import date
from fastapi import APIRouter, Depends

from app.hotels.router import router
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.shemas import SRoom


@router.get("/{hotel_id}/rooms")
def get_rooms():
    pass