from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import NotFoundError
from app.logger import AppLogger
from app.models.products import ProductCreate, ProductResponse, VariantCreate, VariantResponse
from app.repositories.products_repository import ProductsRepository


class ProductsService:
    def __init__(self, repository: ProductsRepository | None = None) -> None:
        self.repository = repository or ProductsRepository()
        self.logger = AppLogger.get_logger(__name__)

    async def list(self, session: AsyncSession) -> list[ProductResponse]:
        rows = await self.repository.list_products(session)
        products = []
        for row in rows:
            variants = await self.repository.list_variants(session, row["id"])
            products.append(
                ProductResponse(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    variants=[VariantResponse(**variant) for variant in variants],
                )
            )
        return products

    async def get_product_context(self, session: AsyncSession, product_id: int) -> dict:
        """Build product-owned context for cross-domain consumers."""
        rows = await self.repository.list_products(session)
        product = next((row for row in rows if row["id"] == product_id), None)
        if product is None:
            raise NotFoundError("Product not found")
        variants = await self.repository.list_variants(session, product_id)
        return {
            "product": dict(product),
            "variants": [dict(variant) for variant in variants],
            "additional_sources": [],
        }

    async def create(
        self,
        session: AsyncSession,
        payload: ProductCreate,
    ) -> ProductResponse:
        try:
            row = await self.repository.create_product(
                session, payload.name.strip(), payload.description,
                payload.variant.name.strip(), payload.variant.specs.strip(),
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        self.logger.info("product created product_id=%s", row["id"])
        return ProductResponse(**row, variants=[VariantResponse(id=row["product_variant_id"], name=payload.variant.name.strip(), specs=payload.variant.specs.strip())])

    async def add_variant(
        self,
        session: AsyncSession,
        product_id: int,
        payload: VariantCreate,
    ) -> VariantResponse:
        if not await self.repository.product_exists(session, product_id):
            raise NotFoundError("Product not found")
        try:
            row, _ = await self.repository.create_variant(session, product_id, payload.name.strip(), payload.specs.strip())
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        self.logger.info("product variant created product_id=%s variant_id=%s", product_id, row["id"])
        return VariantResponse(**row)
