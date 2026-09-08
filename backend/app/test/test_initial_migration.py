import importlib


EXPECTED_TABLES = {
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


def test_initial_migration_creates_schema_tables_with_audit_columns(monkeypatch) -> None:
    migration = importlib.import_module("database.versions.0001_initial_schema")
    created_tables = {}

    def capture_create_table(name, *elements, **kwargs):
        created_tables[name] = elements

    monkeypatch.setattr(migration.op, "create_table", capture_create_table)
    monkeypatch.setattr(migration.op, "create_index", lambda *args, **kwargs: None)

    migration.upgrade()

    assert set(created_tables) == EXPECTED_TABLES
    for elements in created_tables.values():
        columns = {element.name for element in elements if hasattr(element, "name")}
        assert {"_id", "createdAt", "updatedAt", "deletedAt"} <= columns


def test_initial_migration_has_expected_relationships(monkeypatch) -> None:
    migration = importlib.import_module("database.versions.0001_initial_schema")
    created_tables = {}

    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda name, *elements, **kwargs: created_tables.setdefault(name, elements),
    )
    monkeypatch.setattr(migration.op, "create_index", lambda *args, **kwargs: None)

    migration.upgrade()

    def foreign_key_targets(table_name):
        return {
            foreign_key.target_fullname
            for element in created_tables[table_name]
            if hasattr(element, "foreign_keys")
            for foreign_key in element.foreign_keys
        }

    assert foreign_key_targets("assignment_questions") == {
        "products._id",
        "assignments._id",
    }
    assert foreign_key_targets("assignment_agent_mapping") == {"agents._id", "assignments._id"}
    assert foreign_key_targets("agent_queries") == {"products._id"}
    assert foreign_key_targets("products") == {"product_lineups._id", "product_variants._id"}
    assert foreign_key_targets("product_variants") == {"product_lineups._id"}
