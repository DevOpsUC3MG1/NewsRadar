# NewsRadar — Agent Guide

## Dev commands

```bash
# Start dev stack (API + MongoDB + Frontend + services)
docker compose -f docker-compose.dev.yml up --build

# Run tests (full stack)
docker compose -f docker-compose.test.yml up --build

# Run backend tests locally (needs Postgres + Mongo running)
pytest backend/tests/ --cov=backend --cov-report=term

# Run integration tests (needs live API at localhost:8000)
pytest tests/test_api.py -v

# Lint
flake8 . --exclude=backend/migrations --max-line-length=120

# Frontend (from frontend/)
npm run dev
```

## Architecture

- **Dual DB**: PostgreSQL (SQLAlchemy async) for users, roles, alerts, categories, sources, RSS channels. MongoDB (motor) for notifications, news articles, keyword cache, wordcloud cache.
- **API prefix**: `/api/v1`
- **Startup order**: `init_db.py` (drop+recreate tables + seed users) → `app.seed` (load RSS sources from `data/rss_sources.json`) → `uvicorn`
- **Auth**: In-memory dict token (not JWT). Seed: `admin@newsradar.com` / `admin123`
- **Two backend apps**: `backend/newsradar_api/app/main.py` (real, DB-backed) and `backend/tests/app/main.py` (standalone mock with in-memory stores)

## Key services (under `backend/newsradar_api/app/services/`)

- **`keyword_service.py`**: Deterministic synonyms from `data/manual_synonyms.json`, IPTC classification by keyword rules (no AI), wordcloud by term frequency.
- **`rss_worker.py`**: RSS feed ingestion for alerts.
- **`analytics_service.py`**: Dashboard stats + wordcloud with MongoDB caching (6h TTL).

## MANUAL_SYNONYMS_FILE quirk

The env var path is resolved **relative to the project root**, not CWD. Set it as:
```
MANUAL_SYNONYMS_FILE=data/manual_synonyms.json
```
If the resolved path doesn't exist, the code logs a warning and falls back to `<project_root>/data/manual_synonyms.json`.

## Testing

- `backend/tests/` — pytest with `TestClient`, fixtures in `backend/tests/fixtures/` and `conftest.py`
- `tests/test_api.py` — integration tests against live API at localhost:8000 (needs full stack up)

## Conventions

- Flake8: max-line-length=120, exclude migrations
- Frontend: JS (no TS), React + Vite, ESLint (react-hooks, react-refresh)
- No pre-commit hooks, no Makefile, no type checker
- Docker compose v3 files, healthchecks on db services
- Three compose files: `.yml` (prod), `.dev.yml` (dev with hot reload), `.test.yml` (test with isolated DB)
