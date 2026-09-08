"""Product-domain adapter for future cross-domain workflows."""

from app.services.products_service import ProductsService


class ProductContextAdapter:
    """Expose an existing ProductsService flow through the context port."""

    def __init__(self, session, service: ProductsService | None = None) -> None:
        self.session = session
        self.service = service or ProductsService()

    async def get_product_context(self, product_id: int) -> dict:
        return await self.service.get_product_context(self.session, product_id)


# Backwards-compatible alias for callers using the original adapter name.
RepositoryProductContext = ProductContextAdapter
