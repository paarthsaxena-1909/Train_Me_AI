import ast
import importlib
import re
from pathlib import Path

import pytest

from app.logger import AppLogger
from app.errors import ForbiddenError
from app.main import create_app
from app.models.auth import Principal
from app.security.dependencies import require_agent
from app.settings import Settings


def test_logger_emits_utc_timestamp_level_name_and_message_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    AppLogger.configure("INFO")
    logger = AppLogger.get_logger("test.logging.contract")

    logger.info("health check complete")

    captured = capsys.readouterr()
    assert captured.err == ""
    assert re.search(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z INFO test\.logging\.contract health check complete\n$",
        captured.out,
    )


def test_logger_filters_messages_below_configured_level(capsys: pytest.CaptureFixture[str]) -> None:
    AppLogger.configure("INFO")
    logger = AppLogger.get_logger("test.logging.level")

    logger.debug("hidden detail")
    logger.warning("visible warning")

    captured = capsys.readouterr()
    assert "hidden detail" not in captured.out
    assert "WARNING test.logging.level visible warning" in captured.out


def test_logger_configuration_is_idempotent_without_duplicate_emission(
    capsys: pytest.CaptureFixture[str],
) -> None:
    AppLogger.configure("INFO")
    AppLogger.configure("INFO")
    logger = AppLogger.get_logger("test.logging.idempotence")

    logger.info("one event")

    captured = capsys.readouterr()
    assert captured.out.count("one event") == 1
    assert len([handler for handler in logger.handlers if handler.name == "train-me-ai-stdout"]) == 1


def test_repeated_app_creation_keeps_one_handler_and_one_event(
    capsys: pytest.CaptureFixture[str],
) -> None:
    AppLogger.configure("INFO")
    logger = AppLogger.get_logger("test.logging.app-creation")

    create_app()
    create_app()
    logger.info("app event")

    captured = capsys.readouterr()
    assert captured.out.count("app event") == 1
    assert len([handler for handler in logger.handlers if handler.name == "train-me-ai-stdout"]) == 1


def test_app_creation_emits_one_safe_lifecycle_record_per_creation(
    capsys: pytest.CaptureFixture[str],
) -> None:
    AppLogger.configure("INFO")

    create_app()
    first = capsys.readouterr().out
    create_app()
    second = capsys.readouterr().out

    assert first.count("application created") == 1
    assert second.count("application created") == 1
    assert "secret" not in first.lower()
    assert "token" not in first.lower()


def test_reloaded_logger_module_reuses_one_managed_handler(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logger_module = importlib.import_module("app.logger.logger")
    logger_module.AppLogger.configure("INFO")
    logger_name = "test.logging.reload"
    logger_module.AppLogger.get_logger(logger_name)

    reloaded_module = importlib.reload(logger_module)
    reloaded_module.AppLogger.configure("INFO")
    logger = reloaded_module.AppLogger.get_logger(logger_name)
    logger.info("reload event")

    captured = capsys.readouterr()
    assert captured.out.count("reload event") == 1
    assert len([handler for handler in logger.handlers if handler.name == "train-me-ai-stdout"]) == 1


def test_logger_can_be_reconfigured_for_debug_events(capsys: pytest.CaptureFixture[str]) -> None:
    AppLogger.configure("DEBUG")
    AppLogger.get_logger("test.logging.debug").debug("debug event")

    captured = capsys.readouterr()
    assert "DEBUG test.logging.debug debug event" in captured.out


def test_settings_reject_invalid_log_level() -> None:
    with pytest.raises(ValueError):
        Settings(log_level="TRACE")


def test_settings_normalize_log_level_from_environment_style_value() -> None:
    assert Settings(log_level="warning").log_level == "WARNING"


def test_role_mismatch_logs_safe_authorization_context(
    capsys: pytest.CaptureFixture[str],
) -> None:
    AppLogger.configure("INFO")

    with pytest.raises(ForbiddenError, match="Agent role required"):
        require_agent(Principal(account_id=42, role="admin"))

    captured = capsys.readouterr()
    assert "WARNING app.security.dependencies authorization rejected" in captured.out
    assert "account_id=42" in captured.out
    assert "current_role=admin" in captured.out
    assert "required_role=agent" in captured.out
    assert "token" not in captured.out.lower()


def test_production_application_code_has_no_print_calls() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    excluded_parts = {"test", "tests", ".venv", "__pycache__", ".pytest_cache", "generated"}

    for path in backend_root.rglob("*.py"):
        if excluded_parts.intersection(path.parts):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and (
                (isinstance(node.func, ast.Name) and node.func.id == "print")
                or (isinstance(node.func, ast.Attribute) and node.func.attr == "print")
            ):
                raise AssertionError(f"production print call found in {path}:{node.lineno}")
