from datetime import date
from fastapi import APIRouter, Depends

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.exceptions import RoomCannotBeBooked


router = APIRouter(
    prefix="/bookings",  # находится перед всеми ендпоинтами
    tags=["Бронирование"]  # название роутера для документации 
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)): #-> List[SBooking]: 
    bookings_orm = await BookingDAO.find_all(user_id=user.id)
    bookings = [SBooking(**booking["Bookings"].__dict__) for booking in bookings_orm]
    return bookings


@router.post("")
async def add_booking(
    room_id: int, date_from: date, date_to: date,
    user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked
