"""Safe mocked OpenAI-provider failure checks; they never call the network."""

import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from backend.controllers.openai_controller import ModelProviderError, OpenAIController


class OpenAIControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.messages = [{"role": "user", "content": "Test the safe error handling."}]

    @patch("backend.controllers.openai_controller.config.OPENAI_API_KEY", "test-key")
    @patch("backend.controllers.openai_controller.urlopen")
    def test_rate_limit_is_reported_without_a_real_request(self, mocked_urlopen) -> None:
        mocked_urlopen.side_effect = HTTPError("https://api.openai.com/v1/responses", 429, "rate limit", None, None)
        with self.assertRaisesRegex(ModelProviderError, "rate limit"):
            OpenAIController().complete(self.messages, 50)
        mocked_urlopen.assert_called_once()

    @patch("backend.controllers.openai_controller.config.OPENAI_API_KEY", "test-key")
    @patch("backend.controllers.openai_controller.urlopen")
    def test_provider_failure_is_safe_without_a_real_request(self, mocked_urlopen) -> None:
        mocked_urlopen.side_effect = URLError("simulated outage")
        with self.assertRaisesRegex(ModelProviderError, "provider is unavailable"):
            OpenAIController().complete(self.messages, 50)
        mocked_urlopen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
