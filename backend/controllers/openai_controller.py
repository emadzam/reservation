"""Backend-only OpenAI Responses API adapter; credentials never leave the server."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from backend import config


class ModelProviderError(RuntimeError):
    """A safe, user-facing model-provider failure."""


class OpenAIController:
    """Create non-streaming Responses API requests with the configured model."""

    endpoint = "https://api.openai.com/v1/responses"

    def complete(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        if not config.OPENAI_API_KEY:
            raise ModelProviderError(
                "The chatbot is not configured. Add OPENAI_API_KEY to the local .env file and restart the backend."
            )
        instructions = "\n\n".join(message["content"] for message in messages if message["role"] == "system")
        user_input = "\n\n".join(message["content"] for message in messages if message["role"] != "system")
        payload = json.dumps(
            {
                "model": config.OPENAI_MODEL,
                "instructions": instructions,
                "input": user_input,
                "max_output_tokens": max_tokens,
                "reasoning": {"effort": "medium"},
                "text": {"format": {"type": "text"}},
                "store": False,
            }
        ).encode()
        request = Request(
            self.endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                body: Any = json.load(response)
        except HTTPError as error:
            if error.code in {401, 403}:
                message = "OpenAI rejected the configured API key. Replace OPENAI_API_KEY in .env and restart the backend."
            elif error.code == 429:
                message = "OpenAI's rate limit was reached. Please try again later."
            elif error.code in {400, 404}:
                message = "The configured OpenAI model is unavailable. Check OPENAI_MODEL and try again."
            else:
                message = "The chatbot provider is unavailable. Please try again."
            raise ModelProviderError(message) from error
        except (URLError, OSError, ValueError) as error:
            raise ModelProviderError("The chatbot provider is unavailable. Please try again.") from error
        content = self._output_text(body)
        if not content:
            if isinstance(body, dict) and body.get("status") == "incomplete":
                raise ModelProviderError(
                    "The chatbot response ended before it could provide an answer. Please try the question again."
                )
            raise ModelProviderError("The chatbot provider returned an empty response.")
        return content

    @staticmethod
    def _output_text(body: Any) -> str:
        if isinstance(body, dict) and isinstance(body.get("output_text"), str):
            return body["output_text"].strip()
        if not isinstance(body, dict):
            return ""
        parts: list[str] = []
        for output in body.get("output", []):
            if not isinstance(output, dict):
                continue
            for content in output.get("content", []):
                if isinstance(content, dict) and content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    parts.append(content["text"])
        return "\n".join(parts).strip()
