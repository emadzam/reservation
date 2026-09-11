"""Reservation Lite Part 1 FastAPI service."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"

app = FastAPI(title="Reservation Lite API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def read_csv(filename: str) -> list[dict[str, str]]:
    """Read a project CSV fixture as a list of records."""
    with (DATA_DIRECTORY / filename).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def hotel_stays() -> list[dict[str, Any]]:
    """Join hotels and trips by hotel_id for the search response."""
    hotels = {hotel["hotel_id"]: hotel for hotel in read_csv("hotels.csv")}
    results: list[dict[str, Any]] = []
    for trip in read_csv("trips.csv"):
        hotel = hotels.get(trip["hotel_id"])
        if hotel is None:
            continue
        results.append(
            {
                "hotelId": hotel["hotel_id"],
                "hotelName": hotel["hotel_name"],
                "city": hotel["city"],
                "state": hotel["state"],
                "nightlyRateUsd": float(hotel["nightly_rate_usd"]),
                "tripId": trip["trip_id"],
                "tripName": trip["trip_name"],
                "checkIn": trip["check_in"],
                "checkOut": trip["check_out"],
            }
        )
    return results


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hotels")
def search_hotels(q: str = Query(..., min_length=1, max_length=100)) -> dict[str, Any]:
    """Return offered stays whose hotel name contains q, case-insensitively."""
    query = q.strip().casefold()
    matches = [stay for stay in hotel_stays() if query in stay["hotelName"].casefold()]
    return {"query": q.strip(), "count": len(matches), "results": matches}
