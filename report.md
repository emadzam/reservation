# Reservation Lite — Part 1

## Repository and commit

Repository URL: pending GitHub repository setup. Exact Part 1 commit: pending repository initialization and commit.

## Implementation

Reservation Lite has a Vue browser client in `frontend/` and a Python FastAPI service in `backend/`. The client submits a hotel-name search to `GET /api/hotels`. The backend reads `data/hotels.csv` and `data/trips.csv`, joins records by `hotel_id`, and returns matching hotel stays. The client presents results in a labeled table and gives a clear message when no match exists.

## Verification

Browser verification completed locally on September 11, 2026. Searching for `Harbor` returned the expected two `Harbor View Hotel` stay rows, with dates, available-room counts, and nightly prices in the labeled table. Searching for `No Such Hotel` returned no table rows and displayed: “No hotels or available stays match ‘No Such Hotel’.” The health endpoint also returned `{"status":"ok"}`.

## Project context and next steps

See the [README](README.md), [API contract](docs/api-contract.md), and [project guidance](AGENTS.md). Part 2 is intentionally not implemented: it will introduce SQLite, simulated booking, booking history, and CRUD operations. Remaining Part 1 submission steps are GitHub setup, commit, push, and replacing the pending commit information above.
