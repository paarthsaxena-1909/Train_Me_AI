from database.models.base import Base
from database.models.user import User


def test_schema_models_expose_shared_metadata() -> None:
    assert Base.metadata.schema is None
    assert User.__tablename__ == "users"
    assert set(Base.metadata.tables) == {"users"}
