"""Direct entrypoint for applying Alembic migrations."""

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv


DATABASE_DIR = Path(__file__).resolve().parent
load_dotenv(DATABASE_DIR / ".env")


def run_migrations() -> None:
    """Apply all migrations up to the latest revision."""
    config = Config(str(DATABASE_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    command.upgrade(config, "head")


if __name__ == "__main__":
    run_migrations()
