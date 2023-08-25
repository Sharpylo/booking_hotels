from typing import Optional
from pydantic import BaseModel


class SRoom(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    services: list
    quantity: int
    image_id: int
    
    class Config:
        from_attributes = True
        
        
class SRoomExtended(SRoom):
    total_cost: Optional[int]
    rooms_left: Optional[int]