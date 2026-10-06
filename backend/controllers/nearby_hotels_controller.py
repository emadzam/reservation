"""Live hotel discovery through the Geoapify Places API."""

from __future__ import annotations

import json
import math
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from backend import config
from backend.controllers.location_controller import lookup_zip


SEARCH_RADIUS_METERS = 5_000
RESULT_LIMIT = 20


def find_nearby_hotels(postcode: str) -> dict[str, Any]:
    """Resolve an exact U.S. ZIP then return hotels inside its five-kilometre circle."""
    location_result = lookup_zip(postcode)
    if location_result["status"] != "resolved":
        return location_result
    if not config.GEOAPIFY_API_KEY:
        return {"status": "provider_error"}

    location = location_result["location"]
    latitude, longitude = location["latitude"], location["longitude"]
    query = urlencode(
        {
            "categories": "accommodation.hotel",
            "filter": f"circle:{longitude},{latitude},{SEARCH_RADIUS_METERS}",
            "bias": f"proximity:{longitude},{latitude}",
            "limit": RESULT_LIMIT,
            "apiKey": config.GEOAPIFY_API_KEY,
        }
    )
    try:
        with urlopen("https://api.geoapify.com/v2/places?" + query, timeout=10) as response:
            if response.status != 200:
                return {"status": "provider_error"}
            payload = json.load(response)
    except (URLError, OSError, ValueError):
        return {"status": "provider_error"}

    if not isinstance(payload, dict) or not isinstance(payload.get("features"), list):
        return {"status": "provider_error"}

    hotels = [_hotel_from_feature(feature) for feature in payload["features"]]
    return {"status": "resolved", "searchCenter": location, "hotels": [hotel for hotel in hotels if hotel]}


def _hotel_from_feature(feature: object) -> dict[str, Any] | None:
    """Convert valid provider data without inventing hotel attributes."""
    if not isinstance(feature, dict):
        return None
    properties = feature.get("properties")
    geometry = feature.get("geometry")
    if not isinstance(properties, dict) or not isinstance(geometry, dict):
        return None
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        return None
    longitude, latitude = coordinates[0], coordinates[1]
    if not _is_coordinate(latitude, 90) or not _is_coordinate(longitude, 180):
        return None
    name = properties.get("name")
    address = properties.get("formatted") or properties.get("address_line1")
    hotel: dict[str, Any] = {"latitude": latitude, "longitude": longitude}
    if isinstance(name, str) and name.strip():
        hotel["name"] = name.strip()
    else:
        hotel["name"] = "Hotel name unavailable"
    if isinstance(address, str) and address.strip():
        hotel["address"] = address.strip()
    else:
        hotel["address"] = "Location details unavailable"
    place_id = properties.get("place_id")
    if isinstance(place_id, str) and place_id:
        hotel["id"] = place_id
    return hotel


def _is_coordinate(value: object, maximum: int) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and -maximum <= value <= maximum
