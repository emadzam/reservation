"""Mocked checks for the live hotel-discovery controller."""

import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from backend.controllers import nearby_hotels_controller as controller


class NearbyHotelsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.location = {"status": "resolved", "location": {"postcode": "02108", "country_code": "us", "latitude": 42.357, "longitude": -71.063}}
        self.lookup = patch.object(controller, "lookup_zip", return_value=self.location)
        self.lookup_mock = self.lookup.start()
        self.addCleanup(self.lookup.stop)
        self.key = patch.object(controller.config, "GEOAPIFY_API_KEY", "test-key")
        self.key.start()
        self.addCleanup(self.key.stop)
        self.network = patch.object(controller, "urlopen")
        self.open = self.network.start()
        self.addCleanup(self.network.stop)

    def respond(self, payload: object) -> None:
        response = io.BytesIO(json.dumps(payload).encode())
        response.status = 200
        self.open.return_value = response

    def test_exact_zip_center_and_five_kilometre_request(self) -> None:
        self.respond({"features": [{"properties": {"name": "Example Hotel", "formatted": "1 Main St, Boston"}, "geometry": {"coordinates": [-71.064, 42.358]}}]})
        result = controller.find_nearby_hotels("02108")
        self.assertEqual(result["hotels"][0]["name"], "Example Hotel")
        self.assertEqual(result["hotels"][0]["address"], "1 Main St, Boston")
        params = parse_qs(urlsplit(self.open.call_args.args[0]).query)
        self.assertEqual(params["filter"], ["circle:-71.063,42.357,5000"])
        self.assertEqual(params["bias"], ["proximity:-71.063,42.357"])
        self.assertEqual(params["categories"], ["accommodation.hotel"])

    def test_unresolved_zip_does_not_search_a_different_location(self) -> None:
        self.lookup_mock.return_value = {"status": "unresolved"}
        self.assertEqual(controller.find_nearby_hotels("02108"), {"status": "unresolved"})
        self.open.assert_not_called()

    def test_missing_fields_are_honest_and_invalid_places_are_omitted(self) -> None:
        self.respond({"features": [
            {"properties": {}, "geometry": {"coordinates": [-71.064, 42.358]}},
            {"properties": {"name": "Bad"}, "geometry": {"coordinates": ["-71", 42.358]}},
        ]})
        hotels = controller.find_nearby_hotels("02108")["hotels"]
        self.assertEqual(hotels, [{"latitude": 42.358, "longitude": -71.064, "name": "Hotel name unavailable", "address": "Location details unavailable"}])

    def test_provider_failure_is_not_an_empty_success(self) -> None:
        self.respond({"features": None})
        self.assertEqual(controller.find_nearby_hotels("02108"), {"status": "provider_error"})


if __name__ == "__main__":
    unittest.main()
