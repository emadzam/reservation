# Project rules

- Keep the backend in `backend/` and the Vue client in `frontend/`.
- Do not install, upgrade, or commit dependencies unless explicitly requested.
- Keep API contracts documented and coordinate frontend changes with backend contract changes.
- Add configuration through environment variables; never commit secrets.
- Run relevant formatting, linting, and tests before completing implementation work once tooling is established.
- Update `README.md` when setup, architecture, or local development commands change.

## MVC architecture and contracts

- `frontend/` is the View layer: screens, Vue components, browser state, and CSS only. The View calls documented HTTP endpoints and does not access SQLite or CSV files.
- `backend/models/` defines entity fields and relationships. Hotels have many trips; users have many bookings; trips have many bookings; a booking references exactly one user and one trip.
- `backend/controllers/` is the Controller layer. `DatabaseController` owns database connections, foreign-key/reference checks, seed loading, and persistence CRUD. Business controllers call it through public methods and do not issue ad hoc SQL.
- FastAPI routes are controller adapters. They accept Pydantic request contracts, call a controller, and return documented JSON response contracts. Keep contract field names stable unless the API contract and View change together.
- Controllers may call other controllers only through public methods. Models do not import controllers, and Views do not import backend code.
