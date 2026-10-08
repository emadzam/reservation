"""FastAPI routes: the Controller boundary between the Vue View and models."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from backend import config
from backend.controllers.booking_controller import BookingController
from backend.controllers.database_controller import DatabaseController
from backend.controllers.search_controller import SearchController
from backend.controllers.saved_hotel_controller import SavedHotelController
from backend.controllers.hotel_chat_controller import ChatWorkflowError, HotelChatController
from backend.controllers.openai_controller import ModelProviderError
from backend.controllers.location_controller import lookup_zip
from backend.controllers.nearby_hotels_controller import find_nearby_hotels
from backend.models.contracts import BookingCreate, BookingStatusUpdate, HotelQuestion, SavedHotelCreate


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE_PATH = Path(os.environ.get("RESERVATION_DATABASE_PATH", PROJECT_ROOT / "backend" / "reservation.db"))

database_controller = DatabaseController(DATABASE_PATH, DATA_DIRECTORY)
search_controller = SearchController(database_controller)
booking_controller = BookingController(database_controller)
saved_hotel_controller = SavedHotelController(database_controller)
hotel_chat_controller = HotelChatController(database_controller)

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
    return {
        "status": "ok",
        "geoapify": "key is configured" if config.GEOAPIFY_API_KEY else "key is not configured",
    }


@app.get("/api/hotels")
def search_hotels(q: str = Query(..., min_length=1, max_length=100)) -> dict[str, Any]:
    return search_controller.search(q)


@app.get("/api/demo/zip-location")
def demo_zip_location(postcode: str = Query(..., pattern=r"^[0-9]{5}$")) -> dict[str, Any]:
    result = lookup_zip(postcode)
    if result["status"] == "unresolved":
        raise HTTPException(status_code=404, detail=f"ZIP {postcode} could not be resolved.")
    if result["status"] != "resolved":
        raise HTTPException(status_code=502, detail="The ZIP lookup provider is unavailable. Please try again.")
    return result["location"]


@app.get("/api/nearby-hotels")
def nearby_hotels(zip: str = Query(..., pattern=r"^[0-9]{5}$")) -> dict[str, Any]:
    """Return live hotel places within 5 km of the exact resolved U.S. ZIP center."""
    result = find_nearby_hotels(zip)
    if result["status"] == "unresolved":
        raise HTTPException(status_code=404, detail=f"ZIP {zip} could not be resolved.")
    if result["status"] != "resolved":
        raise HTTPException(status_code=502, detail="The hotel search service is unavailable. Please try again.")
    return {"zip": zip, "searchCenter": result["searchCenter"], "count": len(result["hotels"]), "hotels": result["hotels"]}


@app.get("/api/saved-hotels")
def saved_hotels(zip: str = Query(..., pattern=r"^[0-9]{5}$")) -> dict[str, Any]:
    """Read local saved hotels for one originally searched ZIP; never calls Geoapify."""
    return saved_hotel_controller.for_zip(zip)


@app.post("/api/saved-hotels", status_code=status.HTTP_201_CREATED)
def save_hotel(payload: SavedHotelCreate) -> dict[str, Any]:
    try:
        return saved_hotel_controller.save(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="The hotel could not be saved locally.")


@app.delete("/api/saved-hotels/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_saved_hotel(hotel_id: str) -> None:
    try:
        removed = saved_hotel_controller.remove(hotel_id)
    except Exception:
        raise HTTPException(status_code=500, detail="The local hotel could not be removed.")
    if not removed:
        raise HTTPException(status_code=404, detail="Saved hotel not found.")


@app.post("/api/hotel-chat")
def hotel_chat(payload: HotelQuestion) -> dict[str, Any]:
    """Answer a question with two backend-only model calls and checked local retrieval."""
    try:
        return hotel_chat_controller.answer(payload.question)
    except (ChatWorkflowError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error))
    except ModelProviderError as error:
        raise HTTPException(status_code=502, detail=str(error))


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
