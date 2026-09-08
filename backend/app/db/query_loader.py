from pathlib import Path


QUERIES_ROOT = Path(__file__).resolve().parent.parent / "queries"


def load_query(service: str, query_name: str) -> str:
    if not service.isidentifier() or not query_name.isidentifier():
        raise ValueError("invalid SQL query name")
    query_path = QUERIES_ROOT / "postgres" / service / f"{query_name}.sql"
    try:
        return query_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as error:
        raise FileNotFoundError(f"SQL query not found: {service}/{query_name}.sql") from error
