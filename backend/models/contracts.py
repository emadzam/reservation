"""Input contracts accepted by controllers from the View/API layer."""

from typing import Literal

from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=50)
    trip_id: str = Field(min_length=1, max_length=50)


class BookingStatusUpdate(BaseModel):
    status: Literal["cancelled"]


class SavedHotelCreate(BaseModel):
    hotel_id: str = Field(min_length=1, max_length=500)
    name: str | None = Field(default=None, max_length=500)
    address: str | None = Field(default=None, max_length=1000)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    zip: str = Field(pattern=r"^[0-9]{5}$")
    search_latitude: float = Field(ge=-90, le=90)
    search_longitude: float = Field(ge=-180, le=180)
    search_locality: str | None = Field(default=None, max_length=500)


class HotelQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500)
