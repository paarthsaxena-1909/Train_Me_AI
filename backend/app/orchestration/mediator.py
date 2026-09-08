"""Small typed mediator for cross-domain application workflows."""

from typing import Any

from app.errors import AppError
from app.orchestration.ports import DomainPort


class DuplicateRouteError(AppError):
    """Raised when an orchestration route is registered more than once."""

    status_code = 409


class MissingRouteError(AppError):
    """Raised when a request targets an unregistered orchestration route."""

    status_code = 404


# Descriptive aliases for callers that prefer explicit registration wording.
DuplicateRouteRegistrationError = DuplicateRouteError
RouteAlreadyRegisteredError = DuplicateRouteError
RouteNotFoundError = MissingRouteError
RouteNotRegisteredError = MissingRouteError


class ServiceMediator:
    """Dispatch async payloads to handlers registered under stable route names."""

    def __init__(self) -> None:
        self._handlers: dict[str, DomainPort[Any, Any]] = {}

    def register(self, name: str, handler: DomainPort[Any, Any]) -> None:
        if name in self._handlers:
            raise DuplicateRouteError(f"Orchestration route already registered: {name}")
        self._handlers[name] = handler

    async def request(self, name: str, payload: Any) -> Any:
        try:
            handler = self._handlers[name]
        except KeyError as error:
            raise MissingRouteError(f"Orchestration route not registered: {name}") from error
        return await handler(payload)
