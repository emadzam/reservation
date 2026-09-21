# Reservation Lite API contract — Part 2

All endpoints are served by FastAPI and persist application records in SQLite. The database path defaults to `backend/reservation.db` and can be set with `RESERVATION_DATABASE_PATH`.

## MVC contracts

The Vue View sends HTTP requests only; it does not access CSV files or SQLite. FastAPI routes adapt HTTP input to the Search and Booking controllers. Those business controllers call the Database controller through public methods. The Database controller returns JSON-ready records and enforces the hotel-to-trip and user/trip-to-booking references before writes.

## Search and users

- `GET /api/hotels?q={hotelName}` searches hotel names case-insensitively and returns joined hotel/trip stays.
- `GET /api/users` returns selectable seeded users as `{ "users": [{ "userId", "userName" }] }`.

## Bookings

- `GET /api/bookings` returns booking history, including joined traveler, hotel, trip, dates, and status fields.
- `POST /api/bookings` accepts `{ "user_id": "U001", "trip_id": "T001" }`, stores a confirmed booking with a unique `B###` ID, and returns HTTP 201.
- `PATCH /api/bookings/{bookingId}` accepts `{ "status": "cancelled" }`. It retains the booking row and returns its changed status.
- `DELETE /api/bookings/{bookingId}` deletes the selected test booking and returns HTTP 204.

Unknown users, trips, or booking IDs return HTTP 404. Invalid request bodies return HTTP 422.
