from database.models import Base


def test_schema_models_expose_shared_metadata() -> None:
    assert Base.metadata.schema is None
    assert set(Base.metadata.tables) == {
        "agents",
        "admins",
        "blob_items",
        "assignment_questions",
        "assignments",
        "assignment_agent_mapping",
        "agent_queries",
        "products",
        "product_lineups",
        "product_variants",
    }


def test_schema_models_use_shared_audit_columns_and_ids() -> None:
    for table in Base.metadata.tables.values():
        assert {"_id", "createdAt", "updatedAt", "deletedAt"} <= set(table.c.keys())
        assert table.c._id.primary_key
