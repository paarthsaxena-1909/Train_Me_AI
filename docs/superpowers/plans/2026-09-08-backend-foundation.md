# Backend Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a typed FastAPI backend with SQLAlchemy-defined schema, Alembic migrations, direct SQL-file query execution, Docker orchestration, and maintainability documentation.

**Architecture:** `backend/app` contains MVC/application code, Pydantic models, repositories, and service-scoped SQL files. `backend/database` owns SQLAlchemy schema models and Alembic migration history. Runtime reads use parameterized SQL files; SQLAlchemy is used for schema metadata and migrations only.

**Tech Stack:** Python 3.12, FastAPI, Pydantic Settings, asyncpg, SQLAlchemy/Alembic, pytest, Docker Compose, PostgreSQL.

**Spec:** Approved backend foundation design in the conversation.

## Global Constraints

- Keep prototype code separate and experimental.
- Every runtime SQL query is its own `.sql` file under `backend/app/queries/<service>/`.
- ORM models are schema documentation and migration metadata, not the runtime repository API.
- Pydantic models are used for API contracts and typed validation.
- Database migrations must complete before backend startup; backend health must pass before frontend startup.

### Task 1: Backend and database foundation

**Files:** Create the backend Dockerfile, dependency/config files, typed app modules, SQL loader, database session factory, ORM base, and initial Alembic migration.

**Verification:** `pytest -q` and Python import checks.

### Task 2: Compose orchestration and frontend container

**Files:** Modify `docker-compose.yml`; create `frontend/Dockerfile`.

**Verification:** `docker compose config`.

### Task 3: Tests, Mermaid docs, README, and backend skill

**Files:** Create backend tests, `backend/app/docs/`, `backend/skills/backend-development/SKILL.md`, and root `README.md`.

**Verification:** test suite, skill validator, and compose config.
