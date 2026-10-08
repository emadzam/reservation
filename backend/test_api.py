"""MVC controller checks against a disposable SQLite database."""

import sqlite3
import tempfile
from contextlib import closing
import unittest
from pathlib import Path

from backend.controllers.booking_controller import BookingController
from backend.controllers.database_controller import DatabaseController
from backend.controllers.search_controller import SearchController


class ReservationControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        project_root = Path(__file__).resolve().parents[1]
        self.database = DatabaseController(
            Path(self.temporary_directory.name) / "reservation-test.db",
            project_root / "data",
        )
        self.database.initialize_database()
        self.search = SearchController(self.database)
        self.bookings = BookingController(self.database)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_search_and_booking_crud(self) -> None:
        self.assertEqual(self.search.search("Harbor")["count"], 2)
        seeded_count = len(self.bookings.history()["bookings"])

        created = self.bookings.create("U003", "T009")
        self.assertIsNotNone(created)
        booking_id = created["bookingId"]

        self.assertTrue(self.bookings.cancel(booking_id))
        self.assertIn(booking_id, [booking["bookingId"] for booking in self.bookings.history()["bookings"]])
        self.assertTrue(self.bookings.delete(booking_id))
        self.assertEqual(len(self.bookings.history()["bookings"]), seeded_count)

    def test_invalid_references_are_rejected(self) -> None:
        self.assertIsNone(self.bookings.create("missing-user", "T001"))
        self.assertIsNone(self.bookings.create("U001", "missing-trip"))

    def test_live_hotel_schema_is_additive_and_enforces_constraints(self) -> None:
        with closing(self.database.connect()) as connection:
            tables = {
                row["name"]
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            }
            self.assertTrue({"hotels", "trips", "users", "bookings", "saved_hotels", "demo_hotel_nights"} <= tables)

            connection.execute(
                "INSERT INTO saved_hotels (hotel_id, name, address, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                ("provider-place-123", None, None, 40.7936, -77.86),
            )
            connection.execute(
                "INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)",
                ("provider-place-123", "2026-10-06"),
            )
            night = connection.execute(
                "SELECT nightly_rate_cents, rooms_available FROM demo_hotel_nights WHERE hotel_id = ?",
                ("provider-place-123",),
            ).fetchone()
            self.assertEqual((night["nightly_rate_cents"], night["rooms_available"]), (10000, 20))

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)",
                    ("provider-place-123", "2026-10-06"),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)",
                    ("unknown-provider", "2026-10-07"),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO saved_hotels (hotel_id, latitude, longitude) VALUES (?, ?, ?)",
                    ("invalid-location", 91, 0),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)",
                    ("provider-place-123", "2026-02-30"),
                )
            connection.commit()
        self.database.initialize_database()
        with closing(self.database.connect()) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM saved_hotels").fetchone()[0],
                1,
            )

    def test_local_saved_hotel_lifecycle_preserves_existing_demo_values(self) -> None:
        first_hotel = {
            "hotel_id": "geoapify-provider-1", "name": "Local Test Hotel", "address": "1 Test Way",
            "latitude": 40.79, "longitude": -77.86, "zip": "16801",
            "search_latitude": 40.8, "search_longitude": -77.87, "search_locality": "State College",
        }
        second_hotel = {
            "hotel_id": "geoapify-provider-2", "name": "Unrelated Hotel", "address": "2 Test Way",
            "latitude": 42.35, "longitude": -71.06, "zip": "02108",
            "search_latitude": 42.35, "search_longitude": -71.06, "search_locality": "Boston",
        }
        self.assertEqual(self.database.save_live_hotel(first_hotel), {"hotelId": "geoapify-provider-1", "saved": True})
        self.database.save_live_hotel(second_hotel)
        with closing(self.database.connect()) as connection:
            connection.execute(
                "UPDATE demo_hotel_nights SET nightly_rate_cents = 12345, rooms_available = 7 WHERE hotel_id = ? AND stay_date = ?",
                ("geoapify-provider-1", "2026-10-10"),
            )
            connection.commit()

        repeated_hotel = {**first_hotel, "name": "Changed API Name", "zip": "16802", "search_latitude": 40.81}
        self.database.save_live_hotel(repeated_hotel)
        local = self.database.list_saved_hotels_for_zip("16801")
        self.assertEqual(local["count"], 1)
        self.assertEqual(local["hotels"][0]["nights"][0], {"stayDate": "2026-10-10", "nightlyRateCents": 12345, "roomsAvailable": 7})
        self.assertIn("geoapify-provider-1", local["savedProviderIds"])
        self.assertEqual(self.database.list_saved_hotels_for_zip("16802")["count"], 1)

        self.assertTrue(self.database.remove_saved_hotel("geoapify-provider-1"))
        self.assertFalse(self.database.remove_saved_hotel("geoapify-provider-1"))
        with closing(self.database.connect()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM saved_hotels WHERE hotel_id = ?", ("geoapify-provider-1",)).fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM saved_hotel_zip_contexts WHERE hotel_id = ?", ("geoapify-provider-1",)).fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM demo_hotel_nights WHERE hotel_id = ?", ("geoapify-provider-1",)).fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM saved_hotels WHERE hotel_id = ?", ("geoapify-provider-2",)).fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
