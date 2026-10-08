"""Deterministic checks for the two-call grounded hotel chatbot workflow."""

import tempfile
import unittest
from pathlib import Path

from backend.controllers.database_controller import DatabaseController
from backend.controllers.hotel_chat_controller import HotelChatController


class FakeModel:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[tuple[list[dict[str, str]], int]] = []

    def complete(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        self.calls.append((messages, max_tokens))
        return self.responses.pop(0)


class HotelChatControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(__file__).resolve().parents[1]
        self.database = DatabaseController(Path(self.temporary_directory.name) / "chat-test.db", root / "data")
        self.database.initialize_database()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def save_hotel(self) -> None:
        self.database.save_live_hotel({
            "hotel_id": "provider-chat-1", "name": "Chat Hotel", "address": "1 Local Way",
            "latitude": 40.79, "longitude": -77.86, "zip": "16801",
            "search_latitude": 40.8, "search_longitude": -77.87, "search_locality": "State College",
        })

    def test_successful_question_uses_two_model_calls_and_retrieved_rows(self) -> None:
        self.save_hotel()
        model = FakeModel([
            '{"sql":"SELECT h.name, n.stay_date, n.nightly_rate_cents, n.rooms_available FROM saved_hotels h JOIN demo_hotel_nights n ON n.hotel_id = h.hotel_id WHERE n.stay_date = \'2026-10-10\'"}',
            "Chat Hotel has a simulated classroom rate of $100.00 on October 10, with 20 rooms available.",
        ])
        result = HotelChatController(self.database, model).answer("What is available on October 10?")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(len(model.calls), 2)
        self.assertIn("Chat Hotel", model.calls[1][0][1]["content"])

    def test_invalid_model_query_is_rejected_without_a_database_write(self) -> None:
        self.save_hotel()
        model = FakeModel(['{"sql":"DELETE FROM saved_hotels"}'])
        with self.assertRaisesRegex(ValueError, "Only one plain SELECT"):
            HotelChatController(self.database, model).answer("Remove my hotel")
        self.assertEqual(self.database.saved_hotel_count(), 1)
        self.assertEqual(len(model.calls), 1)

    def test_insufficient_data_does_not_call_the_model(self) -> None:
        model = FakeModel([])
        result = HotelChatController(self.database, model).answer("Which hotel costs less?")
        self.assertEqual(result["status"], "insufficient_data")
        self.assertEqual(model.calls, [])


if __name__ == "__main__":
    unittest.main()
