"""Product-domain adapter for future cross-domain workflows."""

from pydantic import ConfigDict, validate_call

from app.models.products import ProductContextResponse
from app.services.products_service import ProductsService


class ProductContextAdapter:
    """Expose an existing ProductsService flow through the context port."""

    def __init__(self, session, service: ProductsService | None = None) -> None:
        self.session = session
        self.service = service or ProductsService()

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
    async def get_product_context(self, product_id: int) -> ProductContextResponse:
        return await self.service.get_product_context(self.session, product_id)


# Backwards-compatible alias for callers using the original adapter name.
RepositoryProductContext = ProductContextAdapter
