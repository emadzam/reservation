# Part 1 handoff

## Completed

- Vue hotel-name search interface in `frontend/`
- FastAPI `GET /api/hotels` endpoint in `backend/`
- CSV join between the supplied hotel and trip data using `hotel_id`
- Browser verification for a matching `Harbor` search and a no-results search

## Current limitation

The application is read-only and reads CSV files on every search. It has no SQLite database, user selection, booking creation, booking history, cancellation, or deletion.

## Next task

For Part 2, seed SQLite with the supplied hotel, trip, user, and booking records. Replace CSV reads with database access, then add frontend-driven booking creation, history, cancellation, and test-booking deletion.
