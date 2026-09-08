# PostgreSQL queries

Runtime queries are currently written for PostgreSQL. Keep the database
dialect explicit in the path so a future database switch can add a separate
implementation without mixing dialects:

Every runtime query gets its own file under:

```text
backend/app/queries/postgres/<service>/<query_name>.sql
```

The query loader explicitly selects the `postgres` folder. Do not add dialect
selection settings or pass a dialect argument through repositories yet;
PostgreSQL is the only supported runtime dialect for now.

Use parameter placeholders supported by SQLAlchemy, for example
`:user_id`. Never interpolate user input into SQL strings.

Repositories inherit from `BaseRepository` and call the loader without knowing
the dialect folder; the current loader resolves PostgreSQL queries:

```python
await self.execute_query(session, "users", "get_user", {"user_id": user_id})
```

Do not use SQLAlchemy ORM query APIs for runtime reads or writes. Keep
PostgreSQL SQL readable, focused, and named after the operation it performs.
If another database is introduced later, add its query tree and update the
loader/database strategy in one place rather than changing every repository.
