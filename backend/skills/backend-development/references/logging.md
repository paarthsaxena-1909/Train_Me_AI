# Logging

Application code uses `AppLogger.get_logger(__name__)` for named loggers. The
shared handler is configured by `create_app()` from the typed `Settings.log_level`
value and writes readable UTC records to stdout.

Log lifecycle and domain events that help operate the service: application
startup, health-check outcomes, account creation, authentication outcomes, and
expected authorization failures. Keep messages concise and structured with
safe identifiers such as role and account ID where useful.

Never log passwords, password hashes, bearer tokens, JWT contents, uploaded
image bytes, or complete request bodies. Do not use `print()` in production
application code. Repeated application creation/configuration must not attach
duplicate handlers or duplicate an event.
