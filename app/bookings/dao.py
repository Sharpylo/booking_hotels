from datetime import date
from sqlalchemy import and_, func, insert, or_, select
from app.bookings.schemas import SBooking

from app.dao.base import BaseDAO
from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.shemas import SRoom

class BookingDAO(BaseDAO):
    model = Bookings
    
    @staticmethod
    async def get_bookings(user: int):
        bookings_orm = await BookingDAO.find_all(user_id=user.id)
        bookings = [SBooking(**booking["Bookings"].__dict__) for booking in bookings_orm]
    
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
                enriched_booking['room'] = {
                    'image_id': matching_room.image_id,
                    'name': matching_room.name,
                    'description': matching_room.description,
                    'services': matching_room.services
                }
                enriched_bookings.append(enriched_booking)
                
        return enriched_bookings
    
    
    @staticmethod
    async def get_rooms(room_id: int):
        rooms_orm = await RoomDAO.find_all()
        rooms = []
        
        for room_data in rooms_orm:
            room_object = room_data['Rooms']  # Access the 'Rooms' key in the dictionary
            if room_object and room_object.id == room_id:  # Add this condition to filter by room_id
                try:
                    # Use room_object.services directly (assuming it's a list)
                    room_services = room_object.services
    
                    s_room = SRoom(
                        id=room_object.id,
                        hotel_id=room_object.hotel_id,
                        name=room_object.name,
                        description=room_object.description,
                        price=room_object.price,
                        services=room_services,
                        quantity=room_object.quantity,
                        image_id=room_object.image_id
                    )
                    rooms.append(s_room)
                except AttributeError:
                    print(f"Invalid room object: {room_object}")
                    
        return rooms
    

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
