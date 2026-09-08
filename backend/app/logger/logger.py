"""Process-wide, stdout-only logging for the application."""

from __future__ import annotations

import logging
import sys
import threading
import time
from typing import ClassVar


_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


class _UtcFormatter(logging.Formatter):
    converter = time.gmtime


class AppLogger:
    """Provide named application loggers with one shared stdout handler."""

    _handler: ClassVar[logging.StreamHandler | None] = None
    _level: ClassVar[int] = logging.INFO
    _lock: ClassVar[threading.RLock] = threading.RLock()
    _handler_name: ClassVar[str] = "train-me-ai-stdout"
    _loggers: ClassVar[set[logging.Logger]] = set()
    _logger_marker: ClassVar[str] = "_train_me_ai_managed"
    _handler_marker: ClassVar[str] = "_train_me_ai_managed"

    @classmethod
    def configure(cls, level: str = "INFO") -> None:
        """Configure the shared handler, safely allowing repeated calls."""
        numeric_level = cls._level_number(level)
        with cls._lock:
            if cls._handler is None:
                cls._handler = cls._find_existing_handler() or cls._create_handler()
            else:
                # Assign directly so repeated pytest capture contexts cannot
                # fail while flushing a stream that has already been closed.
                cls._handler.stream = sys.stdout
            setattr(cls._handler, cls._handler_marker, True)
            cls._remove_duplicate_managed_handlers()
            cls._handler.stream = sys.stdout
            cls._handler.setFormatter(
                _UtcFormatter(
                    "%(asctime)sZ %(levelname)s %(name)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%S",
                )
            )
            cls._handler.setLevel(numeric_level)
            cls._level = numeric_level
            for logger in cls._managed_loggers():
                cls._loggers.add(logger)
                logger.setLevel(numeric_level)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Return a named logger connected to the shared application handler."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("logger name must be a non-empty string")
        with cls._lock:
            if cls._handler is None:
                cls.configure()
            logger = logging.getLogger(name)
            for handler in list(logger.handlers):
                if cls._is_managed_handler(handler) and handler is not cls._handler:
                    logger.removeHandler(handler)
            if cls._handler not in logger.handlers:
                logger.addHandler(cls._handler)
            logger.setLevel(cls._level)
            logger.propagate = False
            setattr(logger, cls._logger_marker, True)
            cls._loggers.add(logger)
            return logger

    @classmethod
    def _create_handler(cls) -> logging.StreamHandler:
        handler = logging.StreamHandler(sys.stdout)
        handler.name = cls._handler_name
        setattr(handler, cls._handler_marker, True)
        return handler

    @classmethod
    def _find_existing_handler(cls) -> logging.StreamHandler | None:
        for logger in cls._all_loggers():
            for handler in logger.handlers:
                if cls._is_managed_handler(handler) and isinstance(handler, logging.StreamHandler):
                    return handler
        return None

    @classmethod
    def _remove_duplicate_managed_handlers(cls) -> None:
        if cls._handler is None:
            return
        for logger in cls._all_loggers():
            for handler in list(logger.handlers):
                if cls._is_managed_handler(handler) and handler is not cls._handler:
                    logger.removeHandler(handler)
            if getattr(logger, cls._logger_marker, False) and cls._handler not in logger.handlers:
                logger.addHandler(cls._handler)

    @classmethod
    def _managed_loggers(cls) -> set[logging.Logger]:
        return {
            logger
            for logger in cls._all_loggers()
            if getattr(logger, cls._logger_marker, False)
        }

    @staticmethod
    def _all_loggers() -> set[logging.Logger]:
        return {
            logger
            for logger in logging.root.manager.loggerDict.values()
            if isinstance(logger, logging.Logger)
        }

    @classmethod
    def _is_managed_handler(cls, handler: logging.Handler) -> bool:
        return bool(
            getattr(handler, cls._handler_marker, False)
            or getattr(handler, "name", None) == cls._handler_name
        )

    @staticmethod
    def _level_number(level: str) -> int:
        if not isinstance(level, str):
            raise ValueError("LOG_LEVEL must be one of CRITICAL, ERROR, WARNING, INFO, or DEBUG")
        normalized = level.strip().upper()
        try:
            return _LEVELS[normalized]
        except KeyError as error:
            raise ValueError(
                "LOG_LEVEL must be one of CRITICAL, ERROR, WARNING, INFO, or DEBUG"
            ) from error
