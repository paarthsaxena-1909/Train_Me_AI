# Health check flow

The health endpoint verifies that the API process is running and that the
backend can reach PostgreSQL. It demonstrates the intended controller →
service → repository → SQL-file boundary.

```mermaid
sequenceDiagram
    participant Browser
    participant API as FastAPI controller
    participant Service as Health service
    participant Repo as Health repository
    participant DB as PostgreSQL

    Browser->>API: GET /health
    API->>Service: check(session)
    Service->>Repo: get_database_time(session)
    Repo->>Repo: load health/database_time.sql
    Repo->>DB: SELECT NOW()
    DB-->>Repo: database_time
    Repo-->>Service: datetime
    Service-->>API: HealthResponse
    API-->>Browser: 200 JSON
```
