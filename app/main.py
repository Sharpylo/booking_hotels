from fastapi import FastAPI, Query
from typing import Optional
from datetime import date

from app.bookings.router import router as router_bookings
from app.users.router import router as router_users
from app.hotels.router import router as router_hotels
from app.hotels.rooms.router import router as router_rooms


app = FastAPI()

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_rooms)


class HotelsSearchArgs:
    def __init__(
        self,
        location: str,
        date_from: date,
        date_to: date,
        has_spa: Optional[bool] = Query(None, description="Whether the hotel has a spa or not (bool).", enum=[True, False]),
        stars: Optional[int] = Query(None, ge=1, le=5, description="Number of stars for the hotel (int)."),
    ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.has_spa = has_spa
        self.stars = stars


