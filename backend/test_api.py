"""MVC controller checks against a disposable SQLite database."""

import tempfile
import unittest
from pathlib import Path

from backend.controllers.booking_controller import BookingController
from backend.controllers.database_controller import DatabaseController
from backend.controllers.search_controller import SearchController


class ReservationControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        project_root = Path(__file__).resolve().parents[1]
        database = DatabaseController(
            Path(self.temporary_directory.name) / "reservation-test.db",
            project_root / "data",
        )
        database.initialize_database()
        self.search = SearchController(database)
        self.bookings = BookingController(database)

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


if __name__ == "__main__":
    unittest.main()
