# AI Travel Planner MVP Starter

This repository now includes a **runnable FastAPI backend starter** so you can test and iterate on the architecture document.

## Run locally (without Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Run with Docker Compose

```bash
docker compose up --build
```

This starts:
- API on `http://127.0.0.1:8000`
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`

## Quick API test

```bash
curl -s http://127.0.0.1:8000/health
```

```bash
curl -s -X POST http://127.0.0.1:8000/v1/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{"origin":"DXB","destination":"BOM","date":"2026-03-10","mode":"flight"}'
```

## Run tests

```bash
cd backend
pytest -q
```

## What is stubbed vs real

- `POST /v1/routes/optimize` currently returns deterministic stub data.
- Next steps are to connect provider adapters, ranking engine, DB persistence, and alert workers as documented in `docs/travel_app_architecture.md`.


## New route-ranking endpoints

- `POST /v1/routes/optimize`: Uses mock provider data + weighted ranking (price/duration/layovers).
- `POST /v1/routes/score`: Accepts a custom list of offers and returns ranked output.

Sample:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/routes/score \
  -H "Content-Type: application/json" \
  -d '{"offers":[{"provider":"a","transport_mode":"flight","total_fare":200,"duration_minutes":100,"layovers":0},{"provider":"b","transport_mode":"flight","total_fare":120,"duration_minutes":300,"layovers":1}]}'
```


## Live provider mode (Amadeus)

1. Fill keys in `backend/.env` (template also in `backend/.env.example`):

```env
AMADEUS_API_KEY=your_key
AMADEUS_API_SECRET=your_secret
AMADEUS_ENV=test
```

2. Export them before running (or use your shell env loading flow):

```bash
cd backend
set -a && source .env && set +a
uvicorn app.main:app --reload --port 8000
```

3. Call optimize endpoint with `mode: flight`. If keys are valid, response will contain:
- `"source": "amadeus"`
Otherwise it safely falls back to `"source": "mock"`.


## INR-first API response for mobile UI

For `POST /v1/routes/optimize`, use:

```json
{
  "origin": "HYD",
  "destination": "CMB",
  "date": "2026-06-10",
  "mode": "flight",
  "preferred_currency": "INR"
}
```

Response format is mobile-card friendly:
- `provider`
- `price` (string, 2 decimals)
- `currency` (INR)
- `duration` (ISO format)
- `segments`
- `label` and `score` for ranking explanation

This is ready for a Flutter list/card UI.
