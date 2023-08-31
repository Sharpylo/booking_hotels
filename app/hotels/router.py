from datetime import date
from typing import Optional
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.exceptions import HotelNotFound
from app.hotels.dao import HotelDAO
from app.hotels.shemas import SHotel


router = APIRouter(
    prefix="/hotels",
    tags=["Отели и комнаты"]
)



@router.get("/{location}")
@cache(expire=30)
async def get_hotels_by_location(
    location: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
):
    hotels = await HotelDAO.find_all(location=location, date_from=date_from, date_to=date_to)
    return hotels

@router.get('/id/{hotel_id}', response_model=SHotel)
async def get_hotel_by_id(hotel_id: int):
    hotel_data = await HotelDAO.find_by_id(hotel_id)
    
    if hotel_data is None:
        raise HotelNotFound
    
    return hotel_data