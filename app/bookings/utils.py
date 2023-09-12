from datetime import date

from sqlalchemy import and_, func, or_, select
from app.bookings.models import Bookings
from app.exceptions import DateError
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.models import Rooms
from app.hotels.rooms.shemas import SRoom


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
async def get_rooms_left_add(session, room_id: int, date_from: date, date_to: date):
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