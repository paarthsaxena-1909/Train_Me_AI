# Train Me AI

Train Me AI contains the frontend prototype and the production-oriented
backend foundation.

## Project layout

- `frontend/` — React/TypeScript prototype and Dockerized frontend.
- `backend/app/` — FastAPI MVC application, Pydantic API models, repositories,
  service-scoped SQL files, tests, and Mermaid flow documentation.
- `backend/database/` — SQLAlchemy schema models and Alembic migration history.
- `backend/.github/environment-management.md` — CI/CD environment-file policy.
- `prototype/` — experimental code used for learning and validation; it is not
  part of the production runtime.

Frontend authentication is available at `/agent/login`, `/agent/signup`,
`/admin/login`, and `/admin/signup`. Login tokens are scoped to the current
browser session in `sessionStorage`; the frontend restores account identity
through `GET /api/v1/auth/me` and clears invalid (401) sessions. See
[`frontend/src/features/auth/README.md`](frontend/src/features/auth/README.md)
for the route and session contract.

## Run the stack

```bash
docker compose up --build
```

Startup is ordered as follows:

1. PostgreSQL becomes healthy.
2. The one-shot `database-migration` service runs `backend/database/main.py`,
   which applies Alembic migrations.
3. The backend starts and must pass `GET /api/v1/health`.
4. The frontend starts after the backend health check succeeds.

The frontend is available at <http://localhost:5173> and the API at
<http://localhost:8000>. Stop the stack with `docker compose down`; add `-v`
only when you intentionally want to remove the local PostgreSQL volume.

## Backend conventions

The current runtime SQL dialect is PostgreSQL. Queries live under
`backend/app/queries/postgres/`, with one readable, parameterized query per
file. SQLAlchemy is used to make the database schema explicit and to provide
Alembic metadata. API contracts use Pydantic models. A database-specific query
tree keeps a future database switch isolated. See
`backend/skills/backend-development/SKILL.md` for the operating rules and
`backend/app/docs/` for flow diagrams.

The backend reads development-safe defaults from `backend/app/settings.py`.
Override values such as `JWT_SECRET`, `ACCESS_TOKEN_MINUTES`, `LOG_LEVEL`,
`UPLOAD_ROOT`, `MAX_UPLOAD_BYTES`, and `APP_TIMEZONE` in Compose when needed.
`LOG_LEVEL` accepts `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` and
defaults to `INFO`. Application logs use named standard-library loggers and
are emitted to stdout in UTC; passwords, tokens, uploaded bytes, and request
bodies are never logged. Uploaded media is stored at `/data/uploads` in the
named `uploads_data` volume and persists until the volume is intentionally
removed. The PostgreSQL data volume and upload volume are not removed by a
regular `docker compose down`.
