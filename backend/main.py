"""FastAPI routes: the Controller boundary between the Vue View and models."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from backend.controllers.booking_controller import BookingController
from backend.controllers.database_controller import DatabaseController
from backend.controllers.search_controller import SearchController
from backend.models.contracts import BookingCreate, BookingStatusUpdate


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE_PATH = Path(os.environ.get("RESERVATION_DATABASE_PATH", PROJECT_ROOT / "backend" / "reservation.db"))

database_controller = DatabaseController(DATABASE_PATH, DATA_DIRECTORY)
search_controller = SearchController(database_controller)
booking_controller = BookingController(database_controller)

app = FastAPI(title="Reservation Lite API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    database_controller.initialize_database()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hotels")
def search_hotels(q: str = Query(..., min_length=1, max_length=100)) -> dict[str, Any]:
    return search_controller.search(q)


@app.get("/api/users")
def list_users() -> dict[str, list[dict[str, str]]]:
    return booking_controller.users()


@app.get("/api/bookings")
def list_bookings() -> dict[str, list[dict[str, Any]]]:
    return booking_controller.history()


@app.post("/api/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingCreate) -> dict[str, str]:
    booking = booking_controller.create(payload.user_id, payload.trip_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="User or trip not found.")
    return booking


@app.patch("/api/bookings/{booking_id}")
def cancel_booking(booking_id: str, payload: BookingStatusUpdate) -> dict[str, str]:
    if not booking_controller.cancel(booking_id):
        raise HTTPException(status_code=404, detail="Booking not found.")
    return {"bookingId": booking_id, "status": payload.status}


@app.delete("/api/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: str) -> None:
    if not booking_controller.delete(booking_id):
        raise HTTPException(status_code=404, detail="Booking not found.")
