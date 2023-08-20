from datetime import date
from sqlalchemy import and_, func, insert, or_, select
from app.dao.base import BaseDAO
from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker

class BookingDAO(BaseDAO):
    model = Bookings

    @staticmethod
    async def _get_rooms_left(session, room_id: int, date_from: date, date_to: date):
        booked_rooms = select(Bookings).where(
            and_(
                Bookings.room_id == room_id,
                or_(
                    and_(
                        Bookings.date_from < date_to,
                        Bookings.date_to > date_from,
                    ),
                )
            )
        ).cte("booked_rooms")

        get_rooms_left = select(
            (Rooms.quantity - func.count(booked_rooms.c.room_id)).label("rooms_left")
        ).select_from(Rooms).join(
            booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True
        ).where(Rooms.id == room_id).group_by(
            Rooms.quantity
        )

        rooms_left = await session.execute(get_rooms_left)
        rooms_left = rooms_left.scalar()

        if rooms_left is None:
            get_total_rooms = select(Rooms.quantity).filter_by(id=room_id)
            total_rooms = await session.execute(get_total_rooms)
            total_rooms: int = total_rooms.scalar()
            rooms_left = total_rooms

        return rooms_left

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        async with async_session_maker() as session:
            rooms_left = await cls._get_rooms_left(session, room_id, date_from, date_to)

            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_bookings = insert(Bookings).values(
                    room_id=room_id,
                    user_id=user_id,
                    date_from=date_from,
                    date_to=date_to,
                    price=price,
                ).returning(Bookings)

                new_booking = await session.execute(add_bookings)
                await session.commit()
                return new_booking.scalar()
            else:
                return None
