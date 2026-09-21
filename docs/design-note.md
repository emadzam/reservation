# Reservation Lite design note — Part 2

The Vue client in `frontend/` owns search input, traveler selection, booking actions, and history rendering. It sends all CRUD actions to FastAPI; it does not store bookings itself.

FastAPI owns SQLite schema creation, idempotent seed loading, validation, generated booking IDs, and database queries. On first startup it imports hotel/trip records and the project user/booking seed records. On later startups, `INSERT OR IGNORE` preserves existing IDs and saved changes without duplicating seed rows.

The backend follows MVC. Entity fields and relationships live in `backend/models/`; `DatabaseController` owns SQL, connections, foreign-key checks, and CRUD; `SearchController` and `BookingController` own their business flows. FastAPI routes adapt HTTP contracts to those controllers. Controllers do not expose database connections to the View.

The application database is `backend/reservation.db` by default and is intentionally ignored by Git. Set `RESERVATION_DATABASE_PATH` for an alternate local database, including isolated test runs.
