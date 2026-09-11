# Reservation Lite API contract — Part 1

## `GET /api/hotels?q={hotelName}`

Searches hotel names case-insensitively. The Python FastAPI backend reads `data/hotels.csv` and `data/trips.csv`, then joins rows using `hotel_id`.

Successful responses return HTTP 200:

```json
{
  "query": "Harbor",
  "count": 2,
  "results": [{ "hotelId": "H100", "hotelName": "Harbor View Hotel", "city": "Boston", "country": "USA", "checkIn": "2026-10-04", "checkOut": "2026-10-07", "availableRooms": 8, "pricePerNight": 189.0 }]
}
```

An unmatched search returns `count: 0` and `results: []`. An omitted or blank `q` is rejected with HTTP 422.
