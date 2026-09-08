"""Protocols used as stable boundaries between domain workflows."""

from typing import Awaitable, Protocol, TypeVar


PayloadT = TypeVar("PayloadT")
ResultT = TypeVar("ResultT")


class DomainPort(Protocol[PayloadT, ResultT]):
    """An async domain operation callable by the application mediator."""

    def __call__(self, payload: PayloadT) -> Awaitable[ResultT]: ...
