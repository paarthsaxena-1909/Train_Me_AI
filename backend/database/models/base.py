from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base for all database schema models.

    Add feature-owned ORM models here as the product schema grows. Runtime
    repositories should continue using the SQL files under app/queries.
    """
