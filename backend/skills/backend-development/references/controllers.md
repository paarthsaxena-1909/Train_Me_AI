# Controllers

Controllers own HTTP concerns only: route declarations, FastAPI dependency
injection, status codes, and translating validated API data into service calls.

All API routes must use the versioned `/api/v1` prefix. Put the prefix on the
router so endpoint declarations remain resource-relative; future versions can
be introduced by registering the same controller structure under `/api/v2`.

Database-backed routes must use the shared alias:

```python
from fastapi import APIRouter

from app.db.session import DbSession


router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(session: DbSession) -> HealthResponse:
    return await health_service.check(session)
```

Do not repeat `Depends(get_db_session)` inline. Do not put SQL or business
rules in controllers. Register new routers in `app/main.py`.
