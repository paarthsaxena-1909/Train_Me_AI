# Services

Services own business rules and coordinate one or more repositories. They do
not know about FastAPI route declarations, SQL file paths, or HTTP response
objects.

Every public service operation must declare a typed Pydantic response and
validate the final value before returning it. Use
`@pydantic.validate_call(validate_return=True)`
for runtime argument validation (with `arbitrary_types_allowed=True` for
request-scoped infrastructure objects), and `ResponseModel.model_validate(...)`
for repository rows or assembled dictionaries. This keeps service contracts
correct even when callers bypass HTTP/controller validation.

```python
class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    async def get_user(self, session: Any, user_id: int) -> UserResponse:
        user = await self.repository.get_by_id(session, user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return UserResponse.model_validate(user)
```

Pass the same request-scoped session to every repository involved in one
operation so transaction boundaries remain consistent. Keep services easy to
test by injecting repository dependencies.
