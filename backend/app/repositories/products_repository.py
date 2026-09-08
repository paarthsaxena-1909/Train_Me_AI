from app.repositories.base_repository import BaseRepository


class ProductsRepository(BaseRepository):
    async def create_product(self, session, name, description, variant_name, variant_specs):
        result = await self.execute_query(session, "products", "create_product", {
            "name": name, "description": description,
            "variant_name": variant_name, "variant_specs": variant_specs,
        })
        return result.mappings().one()

    async def list_products(self, session):
        return (await self.execute_query(session, "products", "list_products")).mappings().all()

    async def create_variant(self, session, product_id, name, specs):
        lineup = await self.execute_query(session, "products", "product_lineup_id", {"product_id": product_id})
        lineup_id = lineup.mappings().one()["product_lineup_id"]
        result = await self.execute_query(
            session,
            "products",
            "create_variant",
            {"product_lineup_id": lineup_id, "name": name, "specs": specs},
        )
        variant = result.mappings().one()
        combination = await self.execute_query(session, "products", "set_product_variant", {
            "product_id": product_id, "variant_id": variant["id"]
        })
        return variant, combination.mappings().one()

    async def list_variants(self, session, product_id):
        result = await self.execute_query(
            session,
            "products",
            "list_variants",
            {"product_id": product_id},
        )
        return result.mappings().all()

    async def product_exists(self, session, product_id):
        result = await self.execute_query(
            session,
            "products",
            "product_exists",
            {"product_id": product_id},
        )
        return result.first() is not None
