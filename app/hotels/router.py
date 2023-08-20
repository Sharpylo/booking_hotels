from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
import json
from collections import defaultdict

from app.hotels.dao import HotelDAO
from app.hotels.shemas import SHotel


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)



@router.get("")
async def get_hotels(
    location: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
):
    hotels_orm = await HotelDAO.find_all(location=location, date_from=date_from, date_to=date_to)
    hotels_dict = defaultdict(dict)

    for hotel in hotels_orm:
        hotel_data = hotel._asdict()
        hotel_id = hotel_data['id']
        if hotel_id not in hotels_dict:
            hotels_dict[hotel_id] = hotel_data
        else:
            hotels_dict[hotel_id]['rooms_left'] += hotel_data['rooms_left']

    hotels = list(hotels_dict.values())

    return hotels