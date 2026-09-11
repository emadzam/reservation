# Reservation Lite

Reservation Lite is a local travel-search application. Part 1 uses Vue in `frontend/` and a Python FastAPI service in `backend/`.

## Starting structure

```text
reservation/
├── AGENTS.md
├── README.md
├── backend/      # FastAPI service
├── data/         # CSV hotel and stay fixtures
├── docs/         # API documentation
├── frontend/     # Vue browser client
├── handoffs/     # Development handoff notes
└── prompts/      # Reusable project prompts
```

## Run locally

Use Python 3.10+ and install the backend packages (for example, in a virtual environment):

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
```

In a second terminal, serve the frontend directory:

```powershell
python -m http.server 5173 --directory frontend
```

Open `http://127.0.0.1:5173`. Search for `Harbor` to see two available stays, or `No Such Hotel` to confirm the no-results state. The client loads Vue 3 from its official browser module CDN; no Node package installation is required.

## API

The Part 1 contract is documented in [docs/api-contract.md](docs/api-contract.md). The FastAPI service reads `data/hotels.csv` and `data/trips.csv` and joins their records by `hotel_id`.

## Scope

Part 1 covers CSV hotel search only. SQLite, booking, booking history, and CRUD actions are reserved for Part 2.
