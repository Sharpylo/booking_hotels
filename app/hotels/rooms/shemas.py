from pydantic import BaseModel, json


class SRoom(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    services: json
    quantity: int
    image_id: int
    
    class Config:
        from_attributes = True