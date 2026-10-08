"""SQLite persistence controller for Reservation Lite models."""

from __future__ import annotations

import csv
import re
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
            self._migrate_live_hotel_storage(connection)
            connection.executemany("INSERT OR IGNORE INTO hotels VALUES (:hotel_id, :hotel_name, :city, :state, :nightly_rate_usd)", hotels)
            connection.executemany("INSERT OR IGNORE INTO trips VALUES (:trip_id, :hotel_id, :trip_name, :check_in, :check_out)", trips)
            connection.executemany("INSERT OR IGNORE INTO users VALUES (:user_id, :display_name)", users)
            connection.executemany("INSERT OR IGNORE INTO bookings VALUES (:booking_id, :user_id, :trip_id, :booked_on, :status)", bookings)
            connection.commit()

    @staticmethod
    def _migrate_live_hotel_storage(connection: sqlite3.Connection) -> None:
        """Add Part 2 live-hotel storage without changing supplied Assignment 1 tables."""
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS saved_hotels (
                hotel_id TEXT PRIMARY KEY,
                name TEXT,
                address TEXT,
                latitude REAL NOT NULL CHECK(
                    typeof(latitude) IN ('integer', 'real') AND latitude >= -90 AND latitude <= 90
                ),
                longitude REAL NOT NULL CHECK(
                    typeof(longitude) IN ('integer', 'real') AND longitude >= -180 AND longitude <= 180
                )
            );
            CREATE TABLE IF NOT EXISTS demo_hotel_nights (
                hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id),
                stay_date TEXT NOT NULL CHECK(
                    length(stay_date) = 10
                    AND stay_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
                    AND strftime('%Y-%m-%d', stay_date) = stay_date
                ),
                nightly_rate_cents INTEGER NOT NULL DEFAULT 10000 CHECK(
                    typeof(nightly_rate_cents) = 'integer' AND nightly_rate_cents >= 0
                ),
                rooms_available INTEGER NOT NULL DEFAULT 20 CHECK(
                    typeof(rooms_available) = 'integer' AND rooms_available >= 0
                ),
                PRIMARY KEY (hotel_id, stay_date)
            );
            CREATE TABLE IF NOT EXISTS saved_hotel_zip_contexts (
                hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id),
                zip TEXT NOT NULL CHECK(zip GLOB '[0-9][0-9][0-9][0-9][0-9]'),
                search_latitude REAL NOT NULL CHECK(
                    typeof(search_latitude) IN ('integer', 'real') AND search_latitude >= -90 AND search_latitude <= 90
                ),
                search_longitude REAL NOT NULL CHECK(
                    typeof(search_longitude) IN ('integer', 'real') AND search_longitude >= -180 AND search_longitude <= 180
                ),
                search_locality TEXT,
                PRIMARY KEY (hotel_id, zip)
            );
            CREATE TRIGGER IF NOT EXISTS validate_demo_hotel_night_date_on_insert
            BEFORE INSERT ON demo_hotel_nights
            WHEN date(julianday(NEW.stay_date)) != NEW.stay_date
            BEGIN
                SELECT RAISE(ABORT, 'stay_date must be a valid YYYY-MM-DD date');
            END;
            CREATE TRIGGER IF NOT EXISTS validate_demo_hotel_night_date_on_update
            BEFORE UPDATE OF stay_date ON demo_hotel_nights
            WHEN date(julianday(NEW.stay_date)) != NEW.stay_date
            BEGIN
                SELECT RAISE(ABORT, 'stay_date must be a valid YYYY-MM-DD date');
            END;
        """)

    def save_live_hotel(self, hotel: dict[str, Any]) -> dict[str, Any]:
        """Persist one provider result, its ZIP context, and fixed demo nights atomically."""
        with closing(self.connect()) as connection:
            try:
                connection.execute("BEGIN")
                connection.execute(
                    """INSERT OR IGNORE INTO saved_hotels
                    (hotel_id, name, address, latitude, longitude) VALUES
                    (:hotel_id, :name, :address, :latitude, :longitude)""",
                    hotel,
                )
                connection.execute(
                    """INSERT OR IGNORE INTO saved_hotel_zip_contexts
                    (hotel_id, zip, search_latitude, search_longitude, search_locality) VALUES
                    (:hotel_id, :zip, :search_latitude, :search_longitude, :search_locality)""",
                    hotel,
                )
                connection.executemany(
                    "INSERT OR IGNORE INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)",
                    [(hotel["hotel_id"], f"2026-10-{day:02d}") for day in range(10, 15)],
                )
                connection.commit()
            except sqlite3.Error:
                connection.rollback()
                raise
        return {"hotelId": hotel["hotel_id"], "saved": True}

    def list_saved_hotels_for_zip(self, postcode: str) -> dict[str, Any]:
        """Return saved results and their original local ZIP-search context."""
        with closing(self.connect()) as connection:
            rows = connection.execute(
                """SELECT h.hotel_id AS id, h.name, h.address, h.latitude, h.longitude,
                    c.search_latitude, c.search_longitude, c.search_locality
                FROM saved_hotel_zip_contexts c
                JOIN saved_hotels h ON h.hotel_id = c.hotel_id
                WHERE c.zip = ? ORDER BY h.name COLLATE NOCASE, h.hotel_id""",
                (postcode,),
            ).fetchall()
            all_saved_ids = [row["hotel_id"] for row in connection.execute("SELECT hotel_id FROM saved_hotels").fetchall()]
            nights_by_hotel: dict[str, list[dict[str, Any]]] = {}
            if rows:
                placeholders = ",".join("?" for _ in rows)
                night_rows = connection.execute(
                    f"""SELECT hotel_id, stay_date AS stayDate,
                    nightly_rate_cents AS nightlyRateCents, rooms_available AS roomsAvailable
                    FROM demo_hotel_nights WHERE hotel_id IN ({placeholders}) ORDER BY hotel_id, stay_date""",
                    tuple(row["id"] for row in rows),
                ).fetchall()
                for night in night_rows:
                    nights_by_hotel.setdefault(night["hotel_id"], []).append(
                        {
                            "stayDate": night["stayDate"],
                            "nightlyRateCents": night["nightlyRateCents"],
                            "roomsAvailable": night["roomsAvailable"],
                        }
                    )

        hotels = [
            {
                "id": row["id"], "name": row["name"], "address": row["address"],
                "latitude": row["latitude"], "longitude": row["longitude"],
                "searchCenter": {
                    "postcode": postcode, "latitude": row["search_latitude"],
                    "longitude": row["search_longitude"], "locality": row["search_locality"],
                },
                "nights": nights_by_hotel.get(row["id"], []),
            }
            for row in rows
        ]
        return {
            "zip": postcode, "count": len(hotels), "hotels": hotels,
            "savedProviderIds": all_saved_ids,
            "searchCenter": hotels[0]["searchCenter"] if hotels else None,
        }

    def remove_saved_hotel(self, hotel_id: str) -> bool:
        """Remove the local provider hotel and only its dependent local records."""
        with closing(self.connect()) as connection:
            try:
                connection.execute("BEGIN")
                exists = connection.execute("SELECT 1 FROM saved_hotels WHERE hotel_id = ?", (hotel_id,)).fetchone()
                if not exists:
                    connection.rollback()
                    return False
                connection.execute("DELETE FROM saved_hotel_zip_contexts WHERE hotel_id = ?", (hotel_id,))
                connection.execute("DELETE FROM demo_hotel_nights WHERE hotel_id = ?", (hotel_id,))
                connection.execute("DELETE FROM saved_hotels WHERE hotel_id = ?", (hotel_id,))
                connection.commit()
                return True
            except sqlite3.Error:
                connection.rollback()
                raise

    def saved_hotel_count(self) -> int:
        with closing(self.connect()) as connection:
            return int(connection.execute("SELECT COUNT(*) FROM saved_hotels").fetchone()[0])

    def execute_hotel_chat_query(self, sql: str) -> list[dict[str, Any]]:
        """Execute one LLM-proposed, bounded read-only query against local Part 2 tables."""
        allowed_tables = {"saved_hotels", "demo_hotel_nights", "saved_hotel_zip_contexts"}
        normalized = " ".join(sql.strip().split())
        lowered = normalized.lower()
        if not lowered.startswith("select ") or ";" in normalized or "--" in normalized or "/*" in normalized:
            raise ValueError("Only one plain SELECT query is allowed.")
        referenced = set(re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)", lowered))
        if not referenced or not referenced <= allowed_tables:
            raise ValueError("The query may use only local saved-hotel tables.")

        def authorizer(action: int, table: str | None, _column: str | None, _database: str | None, _source: str | None) -> int:
            if action == sqlite3.SQLITE_READ:
                return sqlite3.SQLITE_OK if table in allowed_tables else sqlite3.SQLITE_DENY
            if action in {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_FUNCTION}:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        with closing(self.connect()) as connection:
            connection.set_authorizer(authorizer)
            try:
                rows = connection.execute(f"SELECT * FROM ({normalized}) AS bounded_results LIMIT 50").fetchall()
            except sqlite3.Error as error:
                raise ValueError("The proposed query could not be safely run.") from error
            finally:
                connection.set_authorizer(None)
        return [dict(row) for row in rows]

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
