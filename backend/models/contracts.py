"""Input contracts accepted by controllers from the View/API layer."""

from typing import Literal

from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=50)
    trip_id: str = Field(min_length=1, max_length=50)


class BookingStatusUpdate(BaseModel):
    status: Literal["cancelled"]
