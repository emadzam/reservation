# Reservation Lite — Part 2

## Repository and commit

Repository: https://github.com/emadzam/reservation

Branch: `codex/part2-sqlite-bookings`

Part 2 application commit: `2b3f40087f53dbe8e1f4d965f7beb81aff116d20` — `Complete Part 2 SQLite booking workflow`.

## Implementation

Reservation Lite now uses a SQLite database seeded from the supplied `hotels.csv`, `trips.csv`, `users.csv`, and `bookings.csv` files. The backend follows MVC: entity definitions and request contracts are in `backend/models/`; `DatabaseController` owns connections, seed reference checks, foreign keys, and persistence; `SearchController` and `BookingController` handle the search and booking flows; FastAPI routes adapt those controllers to HTTP.

The Vue frontend remains the View layer. It searches hotels, selects a demo traveler, creates a simulated booking, reads booking history, changes a confirmed booking to `cancelled` while retaining it, and deletes a test booking. The API contract is documented in `docs/api-contract.md`.

## Verification

Manual browser verification completed on September 21, 2026.

- Action: Search for `Harbor`.
  - Expected: matching hotel stays appear with a traveler selector and booking actions.
  - Observed: two Harbor Lantern Hotel stays appeared, with all six demo travelers available for selection.
- Action: Create a booking for Demo Traveler 1 and Boston Autumn Weekend.
  - Expected: a new confirmed booking appears in history.
  - Observed: booking `B007` was created and shown in the history table as Confirmed.
- Action: Cancel `B007`.
  - Expected: its status changes to Cancelled and the record remains in history.
  - Observed: the page displayed the cancellation confirmation and retained `B007` with status Cancelled.
- Action: Delete the temporary `B007` booking.
  - Expected: the test booking is removed from history.
  - Observed: the page displayed “Test booking B007 was deleted.” and `B007` no longer appeared in history.

Automated controller tests also passed for search, create, cancel, delete, restart-safe seeding, and rejected user/trip references.

### Screenshots

![Harbor search, traveler selection, and booking choices](<docs/screenshots/Screenshot 2026-09-21 162010.png>)

![Confirmed B007 booking](<docs/screenshots/Screenshot 2026-09-21 162037.png>)

![Cancelled B007 retained in booking history](<docs/screenshots/Screenshot 2026-09-21 162104.png>)

## Project context and next steps

The [README](README.md) contains local run instructions and the MVC layout. The project rules are in [AGENTS.md](AGENTS.md), the architecture decisions are in [docs/design-note.md](docs/design-note.md), and the API input/output contracts are in [docs/api-contract.md](docs/api-contract.md).

The application intentionally uses local demo travelers and simulated bookings only. It has no authentication, payments, availability inventory, or deployment configuration.
