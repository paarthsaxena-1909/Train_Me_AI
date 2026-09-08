# Application logging sequence (IMPLEMENTED)

```mermaid
sequenceDiagram
    participant Config as FastAPI create_app()
    participant Settings as Typed Settings
    participant Logger as AppLogger
    participant Event as Application lifecycle event
    participant Stdout as stdout

    Config->>Settings: Read LOG_LEVEL (default INFO)
    Settings-->>Config: Validated level or validation error
    Config->>Logger: configure(settings.log_level)
    Logger->>Logger: Reuse one process handler (idempotent)
    Event->>Logger: get_logger(__name__).log(level, safe message)
    Logger->>Stdout: UTC timestamp, level, name, message
```

`AppLogger` owns one stdout handler and updates its level when the application
is created again. Authentication logs contain only event outcomes and safe
identifiers; secrets and request bodies are intentionally excluded.
