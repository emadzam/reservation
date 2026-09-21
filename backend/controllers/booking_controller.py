"""Business controller for booking history and booking lifecycle actions."""

from typing import Any

from backend.controllers.database_controller import DatabaseController


class BookingController:
    def __init__(self, database: DatabaseController) -> None:
        self.database = database

    def users(self) -> dict[str, list[dict[str, str]]]:
        return {"users": self.database.list_users()}

    def history(self) -> dict[str, list[dict[str, Any]]]:
        return {"bookings": self.database.list_bookings()}

    def create(self, user_id: str, trip_id: str) -> dict[str, str] | None:
        booking_id = self.database.create_booking(user_id, trip_id)
        return None if booking_id is None else {"bookingId": booking_id, "message": "Booking confirmed."}

    def cancel(self, booking_id: str) -> bool:
        return self.database.update_booking_status(booking_id, "cancelled")

    def delete(self, booking_id: str) -> bool:
        return self.database.delete_booking(booking_id)
