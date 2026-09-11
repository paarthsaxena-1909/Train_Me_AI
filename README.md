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

## Evaluations avatar prototype

Agents can open `/agent/evaluations` to try the stateless voice-to-avatar
prototype. The browser captures speech with the Web Speech API (or accepts
typed input), the backend chooses one of ten fixed practice responses through
a small LangGraph, and the HeyGen LiveAvatar session speaks that response.
No evaluation data is stored in the database.

Configure these backend environment variables before starting an avatar
session:

- `HEYGEN_API_KEY` — HeyGen credential; server-side only.
- `HEYGEN_AVATAR_ID` — the LiveAvatar avatar to start.
- `HEYGEN_AVATAR_NAME` — accepted for compatibility with the existing app env
  file; its value must still be the HeyGen avatar ID, not a display name.
- `HEYGEN_API_URL` — optional; defaults to `https://api.liveavatar.com`.
- `HEYGEN_IS_SANDBOX` — optional boolean, defaults to `false`.

The browser receives only the temporary LiveAvatar session token, never the
API key. Use a current Chromium-based browser for the most reliable speech
recognition support and allow microphone access when prompted.

## Backend conventions

The current runtime SQL dialect is PostgreSQL. Queries live under
`backend/app/queries/postgres/`, with one readable, parameterized query per
file. SQLAlchemy is used to make the database schema explicit and to provide
Alembic metadata. API contracts use Pydantic models. A database-specific query
tree keeps a future database switch isolated. See
`backend/skills/backend-development/SKILL.md` for the operating rules and
[the service documentation index](docs/README.md) for structural notes and per-flow Mermaid diagrams.

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
