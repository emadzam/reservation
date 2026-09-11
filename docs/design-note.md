# Reservation Lite design note — Part 1

## Architecture

The project separates the Vue browser client in `frontend/` from the Python FastAPI service in `backend/`. The client owns search input, loading state, result display, and the no-results message. The API owns CSV reading, joining records, and filtering search results.

## Data flow

`GET /api/hotels?q={hotelName}` reads `data/hotels.csv` and `data/trips.csv`. The backend joins each trip to a hotel with `hotel_id`, filters hotel names case-insensitively, and returns offered stays. The browser renders the response in a table.

## Scope boundary

Part 1 is read-only and uses supplied CSV data. It does not create bookings or persist any changes. SQLite, users, bookings, booking history, and CRUD workflows are deferred to Part 2.
