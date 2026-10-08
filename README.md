# Reservation Lite

Reservation Lite is a local travel-search and simulated-booking application. Vue runs in `frontend/`; FastAPI and SQLite run in `backend/`.

## Run locally

Use Python 3.10+ and install the existing backend packages:

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
```

In a second terminal, serve the client:

```powershell
python -m http.server 5173 --directory frontend
```

Open `http://127.0.0.1:5173`. Assignment 2, Part 1 is the active screen: enter
a five-digit U.S. ZIP code to search live hotels within 5 km of its resolved
postcode center. Select a hotel card or map marker to highlight the same hotel
in both views.

## Backend configuration

`backend/config.py` loads simple `KEY=VALUE` entries from the project-root
`.env` beside `backend/` and `frontend/`, using only the Python standard
library. Set
`GEOAPIFY_API_KEY` there; existing process environment variables take precedence.
Configuration is read when the backend starts. Stop and restart the backend
after editing `.env`; do not rely on development auto-reload for these changes.
`GET /api/health` preserves `status` and adds `geoapify`, reporting only
`key is configured` or `key is not configured`. Missing, empty, and whitespace-only
keys are not configured. This check does not call Geoapify or return the key.

The Part 2 chatbot additionally uses `OPENAI_API_KEY` and, by default,
`OPENAI_MODEL=gpt-6-luna`. Both stay in the backend-only `.env` file. No
additional Python package is required: the backend uses the official OpenAI
Responses API through its existing standard-library HTTPS client. It makes two
non-streaming requests: one proposes SQL and the second writes an answer from
the checked records. Restart FastAPI after changing either chatbot setting.

`backend/controllers/location_controller.py` resolves the exact U.S. ZIP, and
`backend/controllers/nearby_hotels_controller.py` searches Geoapify Places in a
5 km circle around its returned location. The Vue screen calls
`GET /api/nearby-hotels?zip={zip}`; only the backend calls Geoapify. Its response
contract is documented in `docs/api-contract.md`. Run mocked checks with
`.venv/Scripts/python.exe -m unittest backend.test_location backend.test_nearby_hotels`.

## Persistence and data

On first startup, the backend creates `backend/reservation.db` and idempotently seeds hotels, trips, users, and booking fixtures from `data/`. Subsequent starts preserve saved additions, cancellations, and deletions without duplicating seed records. The database is local and ignored by Git.

Assignment 2, Part 2 adds a separate local shortlist for live API results. A
saved provider hotel retains its original ZIP search context and receives
simulated classroom nightly data for October 10–14, 2026. The Vue client checks
`GET /api/saved-hotels?zip={zip}` first; it calls the unchanged live
`/api/nearby-hotels` endpoint only when that local shortlist has no match.
`POST /api/saved-hotels` and `DELETE /api/saved-hotels/{hotelId}` manage the
local shortlist without changing Assignment 1 records.

`POST /api/hotel-chat` accepts a natural-language question and reads only the
saved-hotel, ZIP-context, and demo-night tables. Model-proposed SQL must be one
bounded `SELECT`; SQLite authorizes reads only from those local Part 2 tables.
The chatbot cannot write records or make bookings.

Set `RESERVATION_DATABASE_PATH` to use another SQLite file, such as an isolated test database.

## MVC architecture

- `frontend/` is the View: Vue screens, browser state, and CSS.
- `backend/models/` contains the hotel, trip, traveler, booking, and request-contract definitions.
- `backend/controllers/` contains the SQLite database controller plus Search and Booking business controllers.
- `backend/main.py` exposes FastAPI routes as controller adapters. The Vue client accesses data only through these documented HTTP contracts.

The CSV relationships are hotel → trips and user/trip → bookings. SQLite enforces those references with foreign keys and the database controller checks all seed references before importing data.

## API

The current API contract is in [docs/api-contract.md](docs/api-contract.md). Part 2 supports database-backed hotel search and frontend-driven booking create, history read, cancellation update, and test-booking deletion.
