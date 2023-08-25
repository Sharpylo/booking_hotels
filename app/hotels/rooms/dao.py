from datetime import date
import json
from typing import Optional, List

from app.dao.base import BaseDAO
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker


class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def get_rooms_by_hotel_id(cls, hotel_id: int, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[dict]:
        rooms_orm = await cls.find_all(hotel_id=hotel_id)
        rooms = []

        for room_dict in rooms_orm:
            room_orm = room_dict['Rooms']
            room = {
                "id": room_orm.id,
                "hotel_id": room_orm.hotel_id,
                "name": room_orm.name,
                "description": room_orm.description,
                "services": room_orm.services,
                "price": room_orm.price,
                "quantity": room_orm.quantity,
                "image_id": room_orm.image_id,
                "total_cost": None,
                "rooms_left": None
            }

            if date_from and date_to:
                # Calculate total cost
                days = (date_to - date_from).days
                room["total_cost"] = days * room_orm.price

                # Get rooms_left
                rooms_left_query = cls.get_rooms_left(date_from, date_to)
                async with async_session_maker() as session:
                    result = await session.execute(rooms_left_query)
                    rooms_left_result = result.mappings().all()

                # Filter results based on the hotel_id and room_id parameters
                filtered_result = next((item for item in rooms_left_result if item['hotel_id'] == room_orm.hotel_id and item['room_id'] == room_orm.id), None)

                if filtered_result:
                    room["rooms_left"] = filtered_result.get('rooms_left', 0)  # Update this line

            rooms.append(room)
        return rooms
