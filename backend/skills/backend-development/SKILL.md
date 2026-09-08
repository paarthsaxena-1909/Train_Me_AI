---
name: backend-development
description: Build and maintain this project's FastAPI backend using its MVC layers, typed Pydantic contracts, SQLAlchemy schema models, Alembic migrations, and service-scoped SQL files.
---

# Backend development

Use this file as the entry point and load only the focused reference needed
for the work. This keeps backend changes modular and avoids pulling every
layer's rules into context.

## Shared rules

- Keep production backend application code under `backend/app`.
- Load API configuration from `backend/app/.env` and migration configuration from `backend/database/.env` with `python-dotenv`.
- Keep controllers, services, repositories, SQL files, API models, and schema models in their designated layers.
- Prefix all controller routes with `/api/v1`; keep endpoint paths resource-relative so the API version can be changed centrally.
- Preserve strong typing and run the relevant backend tests before handoff.
- Keep `prototype/` experimental; production backend code does not belong there.
- Add or update a Mermaid sequence diagram under `backend/app/docs` for each non-trivial flow.
- Domain services must not call another domain service directly. Route
  cross-domain workflows through typed ports and `app/orchestration`'s
  `ServiceMediator`; this is an application boundary, not HTTP middleware.

## Reference routing

Load only the references relevant to the requested change:

- HTTP routes and request/response wiring: [controllers.md](references/controllers.md)
- PostgreSQL sessions, pooling, schema models, and migrations: [database.md](references/database.md)
- Pydantic API contracts: [models.md](references/models.md)
- PostgreSQL query files and parameters: [queries.md](references/queries.md)
- Repository execution and persistence boundaries: [repositories.md](references/repositories.md)
- Business logic and orchestration: [services.md](references/services.md)
- Cross-domain ports and mediator: [orchestration.md](references/orchestration.md)
- Application logging and sensitive-data boundaries: [logging.md](references/logging.md)

For a feature spanning multiple layers, load only the references for those
layers and preserve the flow: controller → service → repository → SQL file.
