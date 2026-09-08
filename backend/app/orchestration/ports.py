"""Protocols used as stable boundaries between domain workflows."""

from typing import Awaitable, Protocol, TypeVar
from app.models.products import ProductContextResponse


PayloadT = TypeVar("PayloadT")
ResultT = TypeVar("ResultT")


class DomainPort(Protocol[PayloadT, ResultT]):
    """An async domain operation callable by the application mediator."""

    def __call__(self, payload: PayloadT) -> Awaitable[ResultT]: ...

class ProductContextPort(Protocol):
    """Read-only product context boundary for future assignments and Q&A."""
    async def get_product_context(self, product_id: int) -> ProductContextResponse: ...
