"""ZIP controller checks with synthetic provider responses; no network calls."""

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

from backend.controllers import location_controller as controller


class LocationControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.key = patch.object(controller.config, "GEOAPIFY_API_KEY", "test-key")
        self.key.start()
        self.addCleanup(self.key.stop)
        self.network = patch.object(controller, "urlopen")
        self.open = self.network.start()
        self.addCleanup(self.network.stop)
        self.result = {"postcode": "16802", "country_code": "us", "lat": 40.8, "lon": -77.9}

    def respond(self, payload) -> None:
        response = io.BytesIO(json.dumps(payload).encode())
        response.status = 200
        self.open.return_value = response

    def test_success_and_request_contract(self) -> None:
        self.respond({"results": [{**self.result, "city": "University Park"}]})
        self.assertEqual(controller.lookup_zip("16802"), {
            "status": "resolved", "location": {
                "postcode": "16802", "country_code": "us", "latitude": 40.8,
                "longitude": -77.9, "locality": "University Park",
            },
        })
        args, kwargs = self.open.call_args
        self.assertEqual(parse_qs(urlsplit(args[0]).query), {
            "postcode": ["16802"], "type": ["postcode"], "filter": ["countrycode:us"],
            "format": ["json"], "apiKey": ["test-key"],
        })
        self.assertEqual(kwargs, {"timeout": 10})

    def test_unresolved_and_invalid_coordinates(self) -> None:
        for changes in ({"postcode": "99999"}, {"country_code": "ca"}, {"lat": None},
                        {"lat": True}, {"lat": 91}, {"lon": -181}, {"lat": float("nan")},
                        {"lon": float("inf")}, {"lon": "-77.9"}):
            with self.subTest(changes=changes):
                self.respond({"results": [{**self.result, **changes}]})
                self.assertEqual(controller.lookup_zip("16802"), {"status": "unresolved"})
        self.respond({"results": []})
        self.assertEqual(controller.lookup_zip("16802"), {"status": "unresolved"})

    def test_skips_mismatch_and_locality_is_optional(self) -> None:
        self.respond({"results": [{**self.result, "postcode": "99999"}, self.result]})
        result = controller.lookup_zip("16802")
        self.assertEqual(result["status"], "resolved")
        self.assertNotIn("locality", result["location"])

    def test_provider_failures_are_sanitized(self) -> None:
        for error in (URLError("credential-bearing text"), TimeoutError("private text"),
                      HTTPError("https://example.invalid/?apiKey=test-key", 403, "private", {}, None)):
            self.open.side_effect = error
            self.assertEqual(controller.lookup_zip("16802"), {"status": "provider_error"})
        self.open.side_effect = None
        for payload in ({}, [], {"results": None}):
            self.respond(payload)
            self.assertEqual(controller.lookup_zip("16802"), {"status": "provider_error"})
        response = io.BytesIO(b"not json")
        response.status = 200
        self.open.return_value = response
        self.assertEqual(controller.lookup_zip("16802"), {"status": "provider_error"})

    def test_missing_key_and_invalid_input_do_not_request(self) -> None:
        with patch.object(controller.config, "GEOAPIFY_API_KEY", ""):
            self.assertEqual(controller.lookup_zip("16802"), {"status": "provider_error"})
        with self.assertRaises(ValueError):
            controller.lookup_zip(16802)
        self.open.assert_not_called()
