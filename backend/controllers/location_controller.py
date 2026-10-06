"""U.S. ZIP geocoding, independent of hotels and database persistence."""

import json
import math
import re
from http.client import HTTPException
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from backend import config


def lookup_zip(postcode: str) -> dict:
    """Return resolved/location, unresolved, or provider_error without provider details."""
    if not isinstance(postcode, str) or re.fullmatch(r"[0-9]{5}", postcode) is None:
        raise ValueError("Postcode must be a five-digit ZIP string.")
    if not config.GEOAPIFY_API_KEY:
        return {"status": "provider_error"}

    query = urlencode({
        "postcode": postcode,
        "type": "postcode",
        "filter": "countrycode:us",
        "format": "json",
        "apiKey": config.GEOAPIFY_API_KEY,
    })
    try:
        with urlopen("https://api.geoapify.com/v1/geocode/search?" + query, timeout=10) as response:
            if response.status != 200:
                return {"status": "provider_error"}
            payload = json.load(response)
    except (URLError, OSError, HTTPException, ValueError):
        return {"status": "provider_error"}

    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        return {"status": "provider_error"}
    for result in payload["results"]:
        if not isinstance(result, dict):
            continue
        if result.get("postcode") != postcode or str(result.get("country_code", "")).lower() != "us":
            continue
        latitude, longitude = result.get("lat"), result.get("lon")
        if not all(
            type(value) in (int, float) and -bound <= value <= bound and math.isfinite(value)
            for value, bound in ((latitude, 90), (longitude, 180))
        ):
            continue
        location = {
            "postcode": postcode,
            "country_code": "us",
            "latitude": latitude,
            "longitude": longitude,
        }
        for field in ("city", "town", "village", "hamlet", "locality"):
            locality = result.get(field)
            if isinstance(locality, str) and locality.strip():
                location["locality"] = locality.strip()
                break
        return {"status": "resolved", "location": location}
    return {"status": "unresolved"}
