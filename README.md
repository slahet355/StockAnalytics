# StockAnalytics

Real-Time Multi-Source Crypto/Stock Analytics Dashboard (minimal scaffold)

This repository contains a scaffold for a FastAPI backend that streams live data via WebSockets, async multi-source fetchers, PostgreSQL persistence, Redis caching, a small Tailwind + Alpine frontend, and Docker/dev compose files for local testing.

Quickstart (development):

1. Copy `.env.example` to `.env` and adjust values.
2. Start services with Docker Compose:

```bash
docker-compose up --build
```

3. Open http://localhost:8000 to view the dashboard (serves a simple test page).

What I scaffolded:
- FastAPI app skeleton with a WebSocket endpoint: `app/main.py` and `app/api/ws.py`.
- Async fetcher template using `httpx`: `app/services/fetcher.py`.
- Async DB and Redis helpers: `app/db.py`, `app/cache.py`.
- Minimal frontend: `app/templates/index.html` and `app/static/js/app.js`.
- Dockerfile and `docker-compose.yml` for local Postgres and Redis.

Next steps:
- Implement concrete multi-API fetchers and API key management.
- Create models and migrations for historical data.
- Add Redis pub/sub integration and full WebSocket broadcasting.

See files in the repo for the initial scaffold.

