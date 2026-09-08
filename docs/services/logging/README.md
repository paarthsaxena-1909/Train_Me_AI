# Logging service

`AppLogger` configures standard-library named loggers and one reload-safe stdout handler. `LOG_LEVEL` is validated by settings. Logs use UTC timestamps and safe event metadata; passwords, tokens, uploaded bytes, and request bodies are excluded.

Flow: [configure and emit](flows/configure-and-emit.md). Logging is an application concern and is not a domain-service dependency.
