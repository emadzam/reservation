"""Grounded hotel questions: proposed SQL, checked retrieval, and grounded answer."""

from __future__ import annotations

import json
import re
from typing import Any

from backend.controllers.database_controller import DatabaseController
from backend.controllers.openai_controller import OpenAIController


class ChatWorkflowError(ValueError):
    """A safe error caused by a question or proposed query, not a database write."""


SCHEMA = """saved_hotels(hotel_id, name, address, latitude, longitude)
demo_hotel_nights(hotel_id, stay_date, nightly_rate_cents, rooms_available)
saved_hotel_zip_contexts(hotel_id, zip, search_latitude, search_longitude, search_locality)"""


class HotelChatController:
    """Coordinates the required two-model-call, read-only local-data workflow."""

    def __init__(self, database: DatabaseController, model: OpenAIController | None = None) -> None:
        self.database = database
        self.model = model or OpenAIController()

    def answer(self, question: str) -> dict[str, Any]:
        clean_question = question.strip()
        if self.database.saved_hotel_count() == 0:
            return {"status": "insufficient_data", "answer": "There are no locally saved hotels yet. Search a ZIP and use Add to Local before asking for a comparison.", "proposedSql": None, "records": []}
        proposal = self.model.complete(
            [{"role": "system", "content": "You create one SQLite SELECT query for a local hotel chatbot."}, {"role": "user", "content": self._sql_prompt(clean_question)}],
            max_tokens=1000,
        )
        sql = self._extract_sql(proposal)
        records = self.database.execute_hotel_chat_query(sql)
        answer = self.model.complete(
            [{"role": "system", "content": "Answer only from the supplied local records. Do not invent hotels, prices, availability, or missing nights. Clearly call rates and availability simulated classroom data. If records are empty or incomplete, say so plainly."}, {"role": "user", "content": json.dumps({"question": clean_question, "records": records}, ensure_ascii=False)}],
            max_tokens=1200,
        )
        return {"status": "ok" if records else "no_matches", "answer": answer, "proposedSql": sql, "records": records}

    @staticmethod
    def _sql_prompt(question: str) -> str:
        return f"""Question: {question}

Schema:
{SCHEMA}

Return JSON only: {{\"sql\": \"...\"}}. The query must be one SELECT statement, use only these tables, never access Assignment 1 tables, never modify data, use no comments or semicolon, and return at most the fields needed to answer the question. Dates are ISO YYYY-MM-DD. nightly_rate_cents and rooms_available are simulated classroom values."""

    @staticmethod
    def _extract_sql(proposal: str) -> str:
        candidate = proposal.strip()
        if candidate.startswith("```"):
            candidate = re.sub(r"^```(?:json|sql)?\s*|\s*```$", "", candidate, flags=re.IGNORECASE).strip()
        try:
            parsed = json.loads(candidate)
            sql = parsed.get("sql") if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            sql = candidate
        if not isinstance(sql, str):
            raise ChatWorkflowError("The model did not provide a usable SQL query.")
        return sql.strip()
