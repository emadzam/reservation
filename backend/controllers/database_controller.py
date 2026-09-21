"""SQLite persistence controller for Reservation Lite models."""

from __future__ import annotations

import csv
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


class DatabaseController:
    """Owns database connections, reference checks, seeding, and CRUD operations."""

    def __init__(self, database_path: Path, data_directory: Path) -> None:
        self.database_path = database_path
        self.data_directory = data_directory

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _read_csv(self, filename: str) -> list[dict[str, str]]:
        with (self.data_directory / filename).open(encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    def _check_csv_references(self, trips: list[dict[str, str]], bookings: list[dict[str, str]]) -> None:
        hotel_ids = {row["hotel_id"] for row in self._read_csv("hotels.csv")}
        user_ids = {row["user_id"] for row in self._read_csv("users.csv")}
        trip_ids = {row["trip_id"] for row in trips}
        missing_trip_hotels = {row["hotel_id"] for row in trips} - hotel_ids
        missing_booking_users = {row["user_id"] for row in bookings} - user_ids
        missing_booking_trips = {row["trip_id"] for row in bookings} - trip_ids
        if missing_trip_hotels or missing_booking_users or missing_booking_trips:
            raise ValueError(
                "Invalid CSV references: "
                f"hotel IDs={sorted(missing_trip_hotels)}, user IDs={sorted(missing_booking_users)}, "
                f"trip IDs={sorted(missing_booking_trips)}"
            )

    def initialize_database(self) -> None:
        hotels = self._read_csv("hotels.csv")
        trips = self._read_csv("trips.csv")
        users = self._read_csv("users.csv")
        bookings = self._read_csv("bookings.csv")
        self._check_csv_references(trips, bookings)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS hotels (hotel_id TEXT PRIMARY KEY, hotel_name TEXT NOT NULL, city TEXT NOT NULL, state TEXT NOT NULL, nightly_rate_usd REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS trips (trip_id TEXT PRIMARY KEY, hotel_id TEXT NOT NULL REFERENCES hotels(hotel_id), trip_name TEXT NOT NULL, check_in TEXT NOT NULL, check_out TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, display_name TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS bookings (booking_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id), trip_id TEXT NOT NULL REFERENCES trips(trip_id), booked_on TEXT NOT NULL DEFAULT CURRENT_DATE, status TEXT NOT NULL CHECK(status IN ('confirmed', 'cancelled')));
            """)
            connection.executemany("INSERT OR IGNORE INTO hotels VALUES (:hotel_id, :hotel_name, :city, :state, :nightly_rate_usd)", hotels)
            connection.executemany("INSERT OR IGNORE INTO trips VALUES (:trip_id, :hotel_id, :trip_name, :check_in, :check_out)", trips)
            connection.executemany("INSERT OR IGNORE INTO users VALUES (:user_id, :display_name)", users)
            connection.executemany("INSERT OR IGNORE INTO bookings VALUES (:booking_id, :user_id, :trip_id, :booked_on, :status)", bookings)
            connection.commit()

    def search_stays(self, query: str) -> list[dict[str, Any]]:
        with closing(self.connect()) as connection:
            rows = connection.execute("""SELECT h.hotel_id AS hotelId, h.hotel_name AS hotelName, h.city, h.state, h.nightly_rate_usd AS nightlyRateUsd, t.trip_id AS tripId, t.trip_name AS tripName, t.check_in AS checkIn, t.check_out AS checkOut FROM trips t JOIN hotels h ON h.hotel_id = t.hotel_id WHERE LOWER(h.hotel_name) LIKE LOWER(?) ORDER BY t.check_in, t.trip_id""", (f"%{query}%",)).fetchall()
        return [dict(row) for row in rows]

    def list_users(self) -> list[dict[str, str]]:
        with closing(self.connect()) as connection:
            rows = connection.execute("SELECT user_id AS userId, display_name AS userName FROM users ORDER BY display_name").fetchall()
        return [dict(row) for row in rows]

    def list_bookings(self) -> list[dict[str, Any]]:
        with closing(self.connect()) as connection:
            rows = connection.execute("""SELECT b.booking_id AS bookingId, b.status, b.booked_on AS bookedOn, u.user_id AS userId, u.display_name AS userName, t.trip_id AS tripId, t.trip_name AS tripName, t.check_in AS checkIn, t.check_out AS checkOut, h.hotel_name AS hotelName, h.city, h.state, h.nightly_rate_usd AS nightlyRateUsd FROM bookings b JOIN users u ON u.user_id = b.user_id JOIN trips t ON t.trip_id = b.trip_id JOIN hotels h ON h.hotel_id = t.hotel_id ORDER BY b.booked_on DESC, b.booking_id DESC""").fetchall()
        return [dict(row) for row in rows]

    def create_booking(self, user_id: str, trip_id: str) -> str | None:
        with closing(self.connect()) as connection:
            if not connection.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone() or not connection.execute("SELECT 1 FROM trips WHERE trip_id = ?", (trip_id,)).fetchone():
                return None
            booking_id = self._next_booking_id(connection)
            connection.execute("INSERT INTO bookings (booking_id, user_id, trip_id, status) VALUES (?, ?, ?, 'confirmed')", (booking_id, user_id, trip_id))
            connection.commit()
        return booking_id

    def update_booking_status(self, booking_id: str, status: str) -> bool:
        with closing(self.connect()) as connection:
            result = connection.execute("UPDATE bookings SET status = ? WHERE booking_id = ?", (status, booking_id))
            connection.commit()
        return result.rowcount == 1

    def delete_booking(self, booking_id: str) -> bool:
        with closing(self.connect()) as connection:
            result = connection.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
            connection.commit()
        return result.rowcount == 1

    @staticmethod
    def _next_booking_id(connection: sqlite3.Connection) -> str:
        rows = connection.execute("SELECT booking_id FROM bookings WHERE booking_id GLOB 'B[0-9]*'").fetchall()
        highest = max((int(row["booking_id"][1:]) for row in rows if row["booking_id"][1:].isdigit()), default=0)
        return f"B{highest + 1:03d}"
