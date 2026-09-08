# Database and migrations

Use `backend/app/.env` for FastAPI settings and `backend/database/.env` for
Alembic/PostgreSQL migration settings. For now, both colocated files contain
the same environment-variable set and are loaded with `python-dotenv`.
CI/CD should generate both files from one canonical set; do not duplicate
values in Compose or source code. Specialized variables can be split later.

Run migrations through `backend/database/main.py`. It is the public migration
entrypoint and calls Alembic programmatically. Keep `database/env.py` as the
internal Alembic context adapter; Alembic uses it to bind model metadata and
execute online/offline migration operations.

Keep connection/session mechanics in `backend/app/db`. Use one shared
`AsyncEngine` and `async_sessionmaker`; the pool controls PostgreSQL connection
counts while `DbSession` provides one request-scoped session.

The current and only supported database dialect is PostgreSQL. Define schema
structure with typed SQLAlchemy models in
`backend/database/models`. Use Alembic files in `backend/database/versions` for
all schema changes. Import every model into the Alembic environment so its
metadata is visible. SQLAlchemy schema models are not the runtime query API.
