"""Business controller for hotel stay search."""

from typing import Any

from backend.controllers.database_controller import DatabaseController


class SearchController:
    def __init__(self, database: DatabaseController) -> None:
        self.database = database

    def search(self, hotel_name: str) -> dict[str, Any]:
        query = hotel_name.strip()
        results = self.database.search_stays(query)
        return {"query": query, "count": len(results), "results": results}
