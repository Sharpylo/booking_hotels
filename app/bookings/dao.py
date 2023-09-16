from datetime import date

from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.bookings.schemas import SBooking
from app.bookings.utils import get_rooms, get_rooms_left_add
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import NoRightsToDelete
from app.hotels.rooms.models import Rooms
from app.logger import logger


class BookingDAO(BaseDAO):
    model = Bookings

    get_rooms = get_rooms
    get_rooms_left_add = get_rooms_left_add

    @staticmethod
    async def get_bookings(user: int):
        bookings_orm = await BookingDAO.find_all(user_id=user.id)
        bookings = [
            SBooking(**booking["Bookings"].__dict__) for booking in bookings_orm
        ]

        # Extract room_ids from bookings
        room_ids = set(booking.room_id for booking in bookings)

        rooms = []
        for room_id in room_ids:
            room = await BookingDAO.get_rooms(room_id=room_id)
            rooms.extend(room)

        enriched_bookings = []
        for booking in bookings:
            matching_rooms = [room for room in rooms if room.id == booking.room_id]
            if matching_rooms:
                matching_room = matching_rooms[0]
                enriched_booking = booking.__dict__
                enriched_booking["room"] = {
                    "image_id": matching_room.image_id,
                    "name": matching_room.name,
                    "description": matching_room.description,
                    "services": matching_room.services,
                }
                enriched_bookings.append(enriched_booking)

        return enriched_bookings

    @staticmethod
    async def find_by_id_and_user(booking_id: int, user_id: int):
        bookings_orm = await BookingDAO.find_all(user_id=user_id)
        for booking in bookings_orm:
            if booking["Bookings"].id == booking_id:
                return SBooking(**booking["Bookings"].__dict__)
        return None

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        try:
            async with async_session_maker() as session:
                rooms_left = await cls.get_rooms_left_add(
                    session, room_id, date_from, date_to
                )

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_bookings = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings)
                    )

                    new_booking = await session.execute(add_bookings)
                    await session.commit()
                    return new_booking.scalar()
                else:
                    return None
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)
            

    @classmethod
    async def booking_del_by_id(cls, booking_id: int, user: int):
        bookings_orm = await BookingDAO.find_all(user_id=user.id)
        bookings = [
            SBooking(**booking["Bookings"].__dict__).id for booking in bookings_orm
        ]

        if int(booking_id) in bookings:
            return await cls.del_by_id(id=booking_id)
        else:
            raise NoRightsToDelete
