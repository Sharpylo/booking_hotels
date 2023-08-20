from datetime import date
from typing import Optional
from sqlalchemy import and_, func, select, outerjoin

from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms

class RoomsAvailability:

    @staticmethod
    def get_rooms_left(date_from: Optional[date], date_to: Optional[date]):
        if date_from and date_to:
            booking_filter = and_(Bookings.date_from <= date_to, Bookings.date_to >= date_from)
        elif date_from:
            booking_filter = Bookings.date_from >= date_from
        elif date_to:
            booking_filter = Bookings.date_to <= date_to
        else:
            booking_filter = None
        
        if booking_filter is not None:
            booked_rooms = select(Bookings.room_id).where(booking_filter).cte("booked_rooms")
        else:
            booked_rooms = select(Bookings.room_id).cte("booked_rooms")
            
        get_rooms_left = select(
            Rooms.hotel_id.label("hotel_id"),
            (Rooms.quantity - func.count(booked_rooms.c.room_id)).label("rooms_left")
        ).select_from(Rooms).outerjoin(
            booked_rooms, booked_rooms.c.room_id == Rooms.id
        ).group_by(
            Rooms.hotel_id, Rooms.quantity
        ).having(
            (Rooms.quantity - func.count(booked_rooms.c.room_id)) > 0
        )
        
        return get_rooms_left
