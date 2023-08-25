from app.database import async_session_maker
from sqlalchemy import insert, select

from app.services.room_availability import RoomsAvailability


class BaseDAO:
    model = None
    
    get_rooms_left = RoomsAvailability.get_rooms_left
    
    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()
        
    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()
            
    @classmethod
    async def del_by_id(cls, id: int):
        async with async_session_maker() as session:
            to_delete = await session.get(cls.model, id)

            if to_delete:
                await session.delete(to_delete) 
                await session.commit()  
                return True
            else:
                return False            

            
