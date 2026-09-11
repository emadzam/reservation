# Reservation Lite API contract — Part 1

## `GET /api/hotels?q={hotelName}`

Searches hotel names case-insensitively. The Python FastAPI backend reads `data/hotels.csv` and `data/trips.csv`, then joins rows using `hotel_id`.

Successful responses return HTTP 200:

```json
{
  "query": "Harbor",
  "count": 2,
  "results": [{ "hotelId": "H001", "hotelName": "Harbor Lantern Hotel", "city": "Boston", "state": "MA", "nightlyRateUsd": 150.0, "tripId": "T001", "tripName": "Boston Harbor Weekend", "checkIn": "2026-09-18", "checkOut": "2026-09-20" }]
}
```

An unmatched search returns `count: 0` and `results: []`. An omitted or blank `q` is rejected with HTTP 422.
