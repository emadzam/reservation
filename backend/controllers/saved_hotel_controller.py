"""Business operations for locally saved live hotel results."""

from __future__ import annotations

from typing import Any

from backend.controllers.database_controller import DatabaseController
from backend.models.contracts import SavedHotelCreate


class SavedHotelController:
    """Keeps the route layer independent of SQLite details."""

    def __init__(self, database: DatabaseController) -> None:
        self.database = database

    def save(self, hotel: SavedHotelCreate) -> dict[str, Any]:
        return self.database.save_live_hotel(hotel.model_dump())

    def for_zip(self, postcode: str) -> dict[str, Any]:
        return self.database.list_saved_hotels_for_zip(postcode)

    def remove(self, hotel_id: str) -> bool:
        return self.database.remove_saved_hotel(hotel_id)
