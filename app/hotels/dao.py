from datetime import date
from typing import Optional
from collections import defaultdict
from sqlalchemy.future import select

from app.dao.base import BaseDAO
from app.hotels.models import Hotels
from app.database import async_session_maker



class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(
        cls, 
        location: str, 
        date_from: Optional[date], 
        date_to: Optional[date]
    ):
        async with async_session_maker() as session:
            get_rooms_left_cte = cls.get_rooms_left(date_from=date_from, date_to=date_to)
            cte_alias = get_rooms_left_cte.alias()

            query = select(
                Hotels.id,
                Hotels.name,
                Hotels.location,
                Hotels.services,
                Hotels.rooms_quantity,
                Hotels.image_id,
                cte_alias.c.rooms_left
            ).join(
                cte_alias, cte_alias.c.hotel_id == Hotels.id
            ).where(
                Hotels.location.like(f"%{location}%")
            )

            result = await session.execute(query)
            hotels_orm = result.fetchall()

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