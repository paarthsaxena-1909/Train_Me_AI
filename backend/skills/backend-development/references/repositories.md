# Repositories

Repositories own persistence operations and result-shape mapping. They should
inherit from `BaseRepository`, which hides SQL-file loading and
`session.execute(text(...))` mechanics.

```python
class UserRepository(BaseRepository):
    async def get_by_id(self, session: AsyncSession, user_id: int) -> UserResponse | None:
        result = await self.execute_query(session, "users", "get_user", {"user_id": user_id})
        row = result.mappings().one_or_none()
        return UserResponse(**row) if row else None
```

Repositories receive the request-scoped session from the service/controller
flow. They must not create independent sessions, hide transactions, or contain
HTTP response logic.
