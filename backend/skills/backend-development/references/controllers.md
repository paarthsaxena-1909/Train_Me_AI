# Controllers

Controllers own HTTP concerns only: route declarations, FastAPI dependency
injection, status codes, and translating validated API data into service calls.

Database-backed routes must use the shared alias:

```python
from app.db.session import DbSession


@router.get("/health", response_model=HealthResponse)
async def health_check(session: DbSession) -> HealthResponse:
    return await health_service.check(session)
```

Do not repeat `Depends(get_db_session)` inline. Do not put SQL or business
rules in controllers. Register new routers in `app/main.py`.
