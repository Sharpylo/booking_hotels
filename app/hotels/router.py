from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
import json
from collections import defaultdict

from app.hotels.dao import HotelDAO
from app.hotels.shemas import SHotel


router = APIRouter(
    prefix="/hotels",
    tags=["Отели и комнаты"]
)



@router.get("")
async def get_hotels(
    location: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
):
    hotels = await HotelDAO.find_all(location=location, date_from=date_from, date_to=date_to)
    return hotels