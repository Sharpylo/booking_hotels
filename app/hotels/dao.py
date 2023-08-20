from datetime import date
from typing import Optional
from app.dao.base import BaseDAO

from app.hotels.models import Hotels
from app.database import engine, async_session_maker

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


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

            # alias the CTE for easier reference
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
            return result.fetchall()