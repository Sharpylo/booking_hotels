from datetime import date
from typing import List, Optional

from fastapi import APIRouter

from app.exceptions import HotelNotFound
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.shemas import SRoomExtended

router = APIRouter(prefix="/hotels", tags=["Отели и комнаты"])


@router.get("/{hotel_id}/rooms", response_model=List[SRoomExtended])
async def get_rooms(
    hotel_id: int, date_from: Optional[date] = None, date_to: Optional[date] = None
):
    rooms = await RoomDAO.get_rooms_by_hotel_id(hotel_id, date_from, date_to)
    if not rooms:
        raise HotelNotFound
    return rooms
