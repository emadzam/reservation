# Part 2 MVC scope

Implement Part 2 as a local travel application using Vue, FastAPI, and SQLite.

- Keep Vue screens, components, browser state, and CSS in `frontend/`.
- Put entity definitions in `backend/models/` and database and business logic in `backend/controllers/`.
- Seed SQLite once from the supplied hotel, trip, user, and booking CSV files; after that, application reads and writes use SQLite.
- Support hotel search, creating simulated bookings, viewing booking history, cancelling a booking while retaining it, and deleting a test booking through the frontend.
- Preserve supplied IDs and generate unique IDs for new bookings.
