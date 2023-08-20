from pydantic import BaseModel, Json


class SHotel(BaseModel):
    id: int
    name: str
    location: str
    services: Json
    rooms_quantity: int
    image_id: int
    
    class Config:
        from_attributes = True