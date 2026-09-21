"""Domain entities and their CSV/SQLite relationships."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Hotel:
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float


@dataclass(frozen=True)
class Trip:
    trip_id: str
    hotel_id: str  # References Hotel.hotel_id: one hotel has many trips.
    trip_name: str
    check_in: str
    check_out: str


@dataclass(frozen=True)
class Traveler:
    user_id: str
    display_name: str


@dataclass(frozen=True)
class Booking:
    booking_id: str
    user_id: str  # References Traveler.user_id: one traveler has many bookings.
    trip_id: str  # References Trip.trip_id: one trip has many bookings.
    status: str
    booked_on: str
