from datetime import date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException

from app.database import async_session_maker
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.shemas import SRoomExtended

router = APIRouter(
    prefix="/hotels",
    tags=["Отели и комнаты"]
)



@router.get("/{hotel_id}/rooms", response_model=List[SRoomExtended])
async def get_rooms(
    hotel_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
):
    rooms = await RoomDAO.get_rooms(hotel_id, date_from, date_to)
    if not rooms:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return rooms