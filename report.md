# Reservation Lite — Part 1

## Repository and commit

Repository: https://github.com/emadzam/reservation

Part 1 application commit: `28ca37d64619dd6e843d96144c820b1daad6060d` — `Use supplied Expedia Lite CSV data`.

## Implementation

Reservation Lite is a local travel search application with a Vue frontend in `frontend/` and a Python FastAPI backend in `backend/`. A visitor enters a hotel name and submits the search form. The Vue client sends a `GET /api/hotels?q=...` request to FastAPI, then displays the returned stays in a labeled table.

The backend reads the supplied `data/hotels.csv` and `data/trips.csv` files and joins each trip to its hotel using `hotel_id`. Each result includes the hotel, city and state, offered stay name, check-in date, check-out date, and nightly rate. A search with no matching hotel returns an empty result list, which the frontend presents with a clear no-results message. The API contract is documented in `docs/api-contract.md`.

## Verification

On September 11, 2026, I started the FastAPI service and Vue client locally and checked both required browser cases.

- Action: Search for `Harbor`.
  - Expected: matching supplied hotel stays appear in a clearly labeled table.
  - Observed: two `Harbor Lantern Hotel` stays appeared: `Boston Harbor Weekend` and `Boston Autumn Weekend`, both in Boston, MA, at $150.00 per night.
- Action: Search for `No Such Hotel`.
  - Expected: no rows and a clear no-results message.
  - Observed: no table rows appeared and the page displayed “No hotels or available stays match ‘No Such Hotel’.”

The health endpoint also returned `{"status":"ok"}`.

## Project context and next steps

The project structure, local run commands, and Part 1 scope are documented in `README.md`; the project guidance is in `AGENTS.md`. Part 1 intentionally uses CSV data only. SQLite, simulated booking, booking history, and CRUD actions are outside this checkpoint’s scope and belong to Part 2.
