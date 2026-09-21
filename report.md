# Reservation Lite — Part 2

## Repository and commit

Repository: https://github.com/emadzam/reservation

Branch: `codex/part2-sqlite-bookings`

Part 2 application commit: `2b3f40087f53dbe8e1f4d965f7beb81aff116d20` — `Complete Part 2 SQLite booking workflow`.

## Implementation

Reservation Lite uses a SQLite database initialized using the provided `hotels.csv`, `trips.csv`, `users.csv`, and `bookings.csv` files. The backend uses the MVC pattern where entity classes and request objects can be found in `backend/models/`; the `DatabaseController` manages connections, reference validation on seed, foreign keys, and persistence, `SearchController` and `BookingController` manage search and booking operations respectively, while FastAPI endpoints wrap around them for HTTP integration.

The Vue frontend remains the View part. It allows searching for hotels, choosing a demo user, making a fake booking, listing booking history, changing status of an existing booking to `cancelled` while keeping it, and deleting a test booking. The API contract is described in `docs/api-contract.md`.

## Verification

Manual browser verification:

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

The automated controller tests also passed for search, create, cancel, delete, restart-safe seeding, and rejected user/trip references.

Persistence check:

- Action: Refresh the browser, then restart both local services and reload the page.
  - Expected: the cancelled booking stays in history and the starter data is not duplicated.
  - Observed: `B007` remained Cancelled after both checks, and the six seeded bookings appeared only once.

### Screenshots

![Harbor search, traveler selection, and booking choices](<docs/screenshots/Screenshot 2026-09-21 162010.png>)

![Confirmed B007 booking](<docs/screenshots/Screenshot 2026-09-21 162037.png>)

![Cancelled B007 retained in booking history](<docs/screenshots/Screenshot 2026-09-21 162104.png>)

## Project context and next steps

The [README](README.md) has the local run instructions and the MVC layout. The project rules are in [AGENTS.md](AGENTS.md), the architecture decisions are in [docs/design-note.md](docs/design-note.md), and the API input/output contracts are in [docs/api-contract.md](docs/api-contract.md).

The application intentionally uses local demo travelers and simulated bookings only. It has no authentication, payments, availability inventory, or deployment configuration.
