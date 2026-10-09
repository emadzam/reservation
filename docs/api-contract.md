# Reservation Lite API contract — Part 2

All endpoints are served by FastAPI and persist application records in SQLite. The database path defaults to `backend/reservation.db` and can be set with `RESERVATION_DATABASE_PATH`.

## MVC contracts

The Vue View sends HTTP requests only; it does not access CSV files or SQLite. FastAPI routes adapt HTTP input to the Search and Booking controllers. Those business controllers call the Database controller through public methods. The Database controller returns JSON-ready records and enforces the hotel-to-trip and user/trip-to-booking references before writes.

## ZIP lookup

`GET /api/demo/zip-location?postcode=16802` calls the ZIP controller with the
required five-digit U.S. ZIP string `postcode`. Missing or invalid input returns
HTTP 422 without calling the provider. Leading zeros are preserved. HTTP 200 returns the location object described below, without the
controller status wrapper. Unresolved locations return HTTP 404 with
`{ "detail": "ZIP 16802 could not be resolved." }`. Provider failures return
HTTP 502 with `{ "detail": "The ZIP lookup provider is unavailable. Please try again." }`.
The Vue panel uses the existing backend request helper; only the backend calls
Geoapify. The unresolved error names the requested postcode.

## ZIP controller

`backend.controllers.location_controller.lookup_zip(postcode)` accepts a five-digit
ZIP string; invalid input raises a fixed-message `ValueError`. The demonstration
input is `"16802"`. It uses the configured backend key and `urllib.request` with
a 10-second timeout to call [Geoapify forward geocoding](https://apidocs.geoapify.com/docs/geocoding/)
with `postcode`, `type=postcode`, `filter=countrycode:us`, and `format=json`.

- Success: `{ "status": "resolved", "location": { "postcode": "16802", "country_code": "us", "latitude": 40.8, "longitude": -77.9, "locality": "University Park" } }`
  (illustrative coordinates). Locality is optional, chosen from city, town,
  village, hamlet, then locality.
- No matching result: `{ "status": "unresolved" }`. Only exact postcode matches
  with U.S. country code and finite numeric coordinates within latitude/longitude
  bounds are accepted; booleans and numeric strings are rejected.
- Missing configuration, transport/HTTP errors, invalid JSON, or invalid response
  envelope: `{ "status": "provider_error" }`. Provider errors are distinct from
  a valid result list containing no acceptable location.

No key, request URL, or exception details are returned or logged. Location data
is independent of the priced Hotel model and does not access the database.
Mocked checks: `.venv/Scripts/python.exe -m unittest backend.test_location`.

## Live nearby-hotel search — Assignment 2, Part 1

`GET /api/nearby-hotels?zip=02108` accepts exactly five digits and preserves
leading zeros. FastAPI first resolves that exact U.S. postcode using Geoapify,
then queries Geoapify Places with `categories=accommodation.hotel`,
`filter=circle:{longitude},{latitude},5000`, and a proximity bias using the
same resolved point. It never substitutes a different location when a ZIP is
unresolved.

Successful responses return HTTP 200:

```json
{
  "zip": "02108",
  "searchCenter": { "postcode": "02108", "country_code": "us", "latitude": 42.357, "longitude": -71.063 },
  "count": 1,
  "hotels": [{ "name": "Example Hotel", "address": "1 Main St, Boston", "latitude": 42.358, "longitude": -71.064 }]
}
```

The API hotel fields map directly to the Part 2 persistence schema when a later
feature saves a result: `hotels[].id` → `saved_hotels.hotel_id`, `name` →
`name`, `address` → `address`, `latitude` → `latitude`, and `longitude` →
`longitude`. Provider IDs are preserved exactly. This Part 1 endpoint remains
read-only and does not save a result.

If the exact ZIP cannot be resolved, the API returns HTTP 404. Provider,
configuration, network, or malformed-response failures return HTTP 502. A
successful response with `count: 0` is the only no-nearby-results case. The
response contains no price, rating, room availability, or booking fields. Name
and address use explicit “unavailable” labels only when Geoapify omitted them.

The Vue View calls only this endpoint. Leaflet uses public OpenStreetMap map
tiles, and the Geoapify key remains backend-only in `.env`.

## Part 2 persistence schema (no frontend behavior added)

Database initialization applies an additive, repeatable SQLite migration in
`DatabaseController`. It leaves the supplied `hotels`, `trips`, `users`, and
`bookings` tables and records unchanged, and creates these tables only if they
do not already exist:

- `saved_hotels`: `hotel_id` is the exact API provider ID and primary key;
  `name` and `address` are nullable because the API can omit them; `latitude`
  and `longitude` are required numeric coordinates constrained to their valid
  geographic ranges.
- `demo_hotel_nights`: composite primary key (`hotel_id`, `stay_date`), with
  `hotel_id` a foreign key to `saved_hotels`. `stay_date` uses `YYYY-MM-DD`.
  `nightly_rate_cents` defaults to `10000`, and `rooms_available` defaults to
  `20`; both are nonnegative integers. These are fictional classroom defaults,
  never values supplied by Geoapify.

## Part 2 local shortlist

The frozen Part 1 `GET /api/nearby-hotels` endpoint remains live-search only.
The following endpoints manage a separate local shortlist and never expose the
Geoapify key:

- `GET /api/saved-hotels?zip=16801` returns saved hotels associated with that
  exact searched ZIP. It does not call Geoapify. A successful response includes
  `count`, `hotels`, `searchCenter`, and `savedProviderIds`. Each hotel contains
  its stored `id`, location fields, original `searchCenter`, and five simulated
  `nights` for October 10–14, 2026.
- `POST /api/saved-hotels` accepts the API hotel mapping (`hotel_id`, `name`,
  `address`, `latitude`, `longitude`) plus `zip`, `search_latitude`,
  `search_longitude`, and optional `search_locality`. It preserves the provider
  ID exactly, creates the ZIP association, and inserts the five classroom demo
  nights only when absent. Existing hotel details, rates, and room counts are
  not overwritten.
- `DELETE /api/saved-hotels/{hotelId}` removes that saved hotel, all of its ZIP
  associations, and its demo nights in one SQLite transaction. It does not
  affect supplied Assignment 1 records or unrelated saved hotels.

`nightlyRateCents` and `roomsAvailable` returned from this local shortlist are
fictional classroom data, not API-provided price or availability information.

## Part 2 grounded hotel chatbot

`POST /api/hotel-chat` accepts `{ "question": "..." }`. The Vue client sends
only the question to FastAPI. FastAPI sends the question, limited local schema,
and SQL rules to the backend-only model. It parses the SQL proposal, rejects
anything except one plain `SELECT`, and uses a SQLite authorizer to allow reads
only from `saved_hotels`, `saved_hotel_zip_contexts`, and `demo_hotel_nights`.
Results are bounded to 50 rows. Invalid or disallowed SQL is never executed.

FastAPI sends those two backend-only requests to OpenAI's Responses API using
`OPENAI_MODEL` (default `gpt-6-luna`): first the original question, limited
schema, and SQL rules; then the original question and only the checked records.
The second request produces the answer. Successful responses include
`status`, `answer`, `proposedSql`, and `records`. `status` is
`insufficient_data` when no hotels have been saved and `no_matches` when a
valid query returns no rows. Provider failures return HTTP 502; invalid
proposals return HTTP 422. Rates and room counts remain labeled as simulated
classroom data. The remote model never receives a SQLite connection and cannot
modify data.

Repeat deterministic checks, including the labeled no-match, rate-limit, and
provider-failure mocks, with:

```text
$env:TEMP="$PWD\\.test-temp"; $env:TMP="$PWD\\.test-temp"; .venv\Scripts\python.exe -m unittest backend.test_hotel_chat backend.test_openai_controller -v
```

The fixed labeled fixtures are
[`hotel-chat-success.json`](fixtures/hotel-chat-success.json),
[`hotel-chat-invalid-query.json`](fixtures/hotel-chat-invalid-query.json),
[`hotel-chat-no-match.json`](fixtures/hotel-chat-no-match.json),
[`hotel-chat-rate-limit.json`](fixtures/hotel-chat-rate-limit.json), and
[`hotel-chat-provider-failure.json`](fixtures/hotel-chat-provider-failure.json).

## Health

`GET /api/health` returns HTTP 200 with
`{ "status": "ok", "geoapify": "key is configured" }`.
The `geoapify` field is `key is not configured` when the key is absent, empty,
or whitespace-only. It reports local configuration only; no Geoapify request is
made and no key value is returned.

## Search and users

- `GET /api/hotels?q={hotelName}` searches hotel names case-insensitively and returns joined hotel/trip stays.
- `GET /api/users` returns selectable seeded users as `{ "users": [{ "userId", "userName" }] }`.

## Bookings

- `GET /api/bookings` returns booking history, including joined traveler, hotel, trip, dates, and status fields.
- `POST /api/bookings` accepts `{ "user_id": "U001", "trip_id": "T001" }`, stores a confirmed booking with a unique `B###` ID, and returns HTTP 201.
- `PATCH /api/bookings/{bookingId}` accepts `{ "status": "cancelled" }`. It retains the booking row and returns its changed status.
- `DELETE /api/bookings/{bookingId}` deletes the selected test booking and returns HTTP 204.

Unknown users, trips, or booking IDs return HTTP 404. Invalid request bodies return HTTP 422.
