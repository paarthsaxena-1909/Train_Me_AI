"""Repository-backed product context adapter for future domain workflows."""

from app.errors import NotFoundError
from app.repositories.products_repository import ProductsRepository


class RepositoryProductContext:
    """Expose catalogue context without coupling consumers to ProductsService."""

    def __init__(self, session, repository: ProductsRepository | None = None) -> None:
        self.session = session
        self.repository = repository or ProductsRepository()

    async def get_product_context(self, product_id: int) -> dict:
        products = await self.repository.list_products(self.session)
        product = next((row for row in products if row["id"] == product_id), None)
        if product is None:
            raise NotFoundError("Product not found")

        variants = await self.repository.list_variants(self.session, product_id)
        return {
            "product": dict(product),
            "variants": [dict(variant) for variant in variants],
            "additional_sources": [],
        }
