from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_versioning import version

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.exceptions import (
    BookingNotFound,
    DateError,
    NoRightsToDelete,
    RoomCannotBeBooked,
    TooManyDays,
)
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/bookings",  # находится перед всеми ендпоинтами
    tags=["Бронирование"],  # название роутера для документации
)


@router.get("")
@version(1)
async def get_all_bookings(user: Users = Depends(get_current_user)):
    enriched_bookings = await BookingDAO.get_bookings(user)
    return enriched_bookings


@router.get("/{booking_id}")
@version(1)
async def get_bookings(booking_id: int, user: Users = Depends(get_current_user)):
    booking = await BookingDAO.find_by_id_and_user(booking_id, user.id)
    if not booking:
        raise BookingNotFound
    return booking


@router.post("")
@version(1)
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    if date_from >= date_to:
        raise DateError
    elif (date_to - date_from).days > 30:
        raise TooManyDays
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked
    booking_obj = SBooking.model_validate(booking)
    booking_dict = booking_obj.model_dump()
    send_booking_confirmation_email.delay(booking_dict, user.email)
    return booking_dict


@router.delete("/{booking_id}", status_code=204)
@version(1)
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    try:
        del_booking = await BookingDAO.booking_del_by_id(booking_id, user)
        if del_booking:
            return
        else:
            raise BookingNotFound
    except NoRightsToDelete as e:
        return JSONResponse(content={"error": str(e.detail)}, status_code=403)
