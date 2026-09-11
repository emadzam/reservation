# Reservation Lite — Part 1

## Repository and commit

Repository URL: https://github.com/emadzam/reservation.git

Exact Part 1 implementation commit: `10fe5fab6846404924c45fb0661a55aff2de3684` (`Complete Part 1 CSV hotel search`).

Official supplied-data correction commit: `28ca37d64619dd6e843d96144c820b1daad6060d` (`Use supplied Expedia Lite CSV data`).

## Implementation

Reservation Lite has a Vue browser client in `frontend/` and a Python FastAPI service in `backend/`. The client submits a hotel-name search to `GET /api/hotels`. The backend reads the supplied `data/hotels.csv` and `data/trips.csv`, joins records by `hotel_id`, and returns matching hotel stays. The client presents results in a labeled table and gives a clear message when no match exists.

## Verification

Browser verification completed locally on September 11, 2026 using the supplied CSV files. Searching for `Harbor` returned the two expected `Harbor Lantern Hotel` stays: `Boston Harbor Weekend` and `Boston Autumn Weekend`, each at $150.00 per night. Searching for `No Such Hotel` returned no table rows and displayed: “No hotels or available stays match ‘No Such Hotel’.” The health endpoint also returned `{"status":"ok"}`.

## Project context and next steps

See the [README](README.md), [API contract](docs/api-contract.md), and [project guidance](AGENTS.md). Part 2 is intentionally not implemented: it will introduce SQLite, simulated booking, booking history, and CRUD operations.
