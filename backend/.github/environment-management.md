# Environment variable management

The backend uses one canonical set of environment variables in CI/CD. The
pipeline is responsible for rendering the required environment files into the
two runtime folders:

```text
backend/app/.env       # FastAPI application settings
backend/database/.env  # Alembic/PostgreSQL migration settings
```

The application loads `backend/app/.env` from `app/settings.py`. The migration
entrypoint loads `backend/database/.env` from `database/main.py` (and Alembic's
internal context reads the same file). For now, both files contain the same
environment variables. This keeps each runtime component self-contained while
preventing values from being duplicated manually in source code or Docker
Compose.

The CI/CD pipeline should:

1. Read the canonical environment variables from the CI/CD secret store.
2. Write the same canonical variable set to `backend/app/.env`.
3. Write that same canonical variable set to `backend/database/.env`.
4. Ensure generated `.env` files are not committed to the repository or
   printed in pipeline logs.

Local development may use the example values in the colocated `.env` files;
deployment values must come from the CI/CD secret store.
