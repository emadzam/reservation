# Reservation Lite — Part 1

## Repository and commit

Repository URL: https://github.com/emadzam/reservation.git

Exact Part 1 implementation commit: `10fe5fab6846404924c45fb0661a55aff2de3684` (`Complete Part 1 CSV hotel search`).

Official supplied-data correction commit: `28ca37d64619dd6e843d96144c820b1daad6060d` (`Use supplied Expedia Lite CSV data`).

## Implementation

Reservation Lite has a Vue browser client in `frontend/` and a Python FastAPI service in `backend/`. The client submits a hotel-name se arch to `GET /api/hotels`. The backend reads the supplied `data/hotels.csv` and `data/trips.csv`, joins records by `hotel_id`, and returns matching hotel stays. The client presents results in a labeled table and gives a clear message when no match exists.

## Verification

Browser verification completed locally on September 11, 2026 using the supplied CSV files. Searching for `Harbor` returned the two expected `Harbor Lantern Hotel` stays: `Boston Harbor Weekend` and `Boston Autumn Weekend`, each at $150.00 per night. Searching for `No Such Hotel` returned no table rows and displayed: “No hotels or available stays match ‘No Such Hotel’.” The health endpoint also returned `{"status":"ok"}`.

## Project context and next steps

The [README](README.md) documents the project structure and local run commands. The project rules are in [AGENTS.md](AGENTS.md), the frontend/backend/data decisions are in the [design note](docs/design-note.md), and the selected Part 1 scope is recorded in [prompts/part1-scope.md](prompts/part1-scope.md). The [Part 1 handoff](handoffs/part1-handoff.md) records the completed work and current state.

The current limitation is intentional: Part 1 is read-only and uses CSV files; it has no database, booking flow, booking history, cancellation, or deletion. The next task for Part 2 is to seed SQLite with the supplied hotel, trip, user, and booking records, then implement frontend-driven booking CRUD and history.


