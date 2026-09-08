# Services

Services own business rules and coordinate one or more repositories. They do
not know about FastAPI route declarations, SQL file paths, or HTTP response
objects.

```python
class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def get_user(self, session: AsyncSession, user_id: int) -> UserResponse:
        user = await self.repository.get_by_id(session, user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user
```

Pass the same request-scoped session to every repository involved in one
operation so transaction boundaries remain consistent. Keep services easy to
test by injecting repository dependencies.
