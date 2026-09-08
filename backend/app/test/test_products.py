import pytest
import asyncio
from pathlib import Path
from app.models.products import ProductCreate, VariantCreate
from app.services.products_service import ProductsService
from app.errors import NotFoundError

class Session:
    def __init__(self): self.commits=0; self.rollbacks=0
    async def commit(self): self.commits += 1
    async def rollback(self): self.rollbacks += 1
class Repo:
    def __init__(self): self.products=[]; self.variants=[]
    async def list_products(self, s): return self.products
    async def list_variants(self, s, product_id): return self.variants
    async def product_exists(self, s, product_id): return any(p['id']==product_id for p in self.products)
    async def create_product(self,s,name,description,variant_name,variant_specs):
        row={'id':1,'name':name,'description':description,'product_variant_id':1}; self.products.append(row)
        self.variants.append({'id':1,'name':variant_name,'specs':variant_specs}); return row
    async def create_variant(self,s,product_id,name,specs):
        row={'id':2,'name':name,'specs':specs}; self.variants.append(row); return row, {'id':2}
def test_create_and_list_catalogue():
    async def run():
        repo=Repo(); session=Session(); service=ProductsService(repo)
        product=await service.create(session,ProductCreate(name='Phone', variant=VariantCreate(name='Base',specs='128GB')))
        variant=await service.add_variant(session,1,VariantCreate(name='Pro',specs='256GB'))
        assert product.name=='Phone' and variant.specs=='256GB' and (await service.list(session))[0].variants[0].name=='Base'
    asyncio.run(run())
def test_missing_parent_rejected():
    async def run():
        with pytest.raises(NotFoundError):
            await ProductsService(Repo()).add_variant(Session(),99,VariantCreate(name='x',specs='y'))
    asyncio.run(run())


def test_product_service_builds_context_for_cross_domain_requests():
    async def run():
        repo = Repo()
        session = Session()
        service = ProductsService(repo)
        await service.create(session, ProductCreate(name='Phone', variant=VariantCreate(name='Base', specs='128GB')))

        context = await service.get_context(session, 1)

        assert context['product']['id'] == 1
        assert context['variants'][0]['name'] == 'Base'

    asyncio.run(run())


def test_migration_releases_legacy_required_catalogue_links():
    migration = Path("database/versions/0003_simple_product_catalogue.py").read_text()

    assert 'op.alter_column("product_variants", "product_lineup_id", nullable=True)' in migration
    assert 'op.alter_column("products", "product_lineup_id", nullable=True)' in migration
    assert 'op.alter_column("products", "product_variant_id", nullable=True)' in migration
    assert 'product_variants", "product_id"' not in migration


def test_product_insert_keeps_lineup_reference():
    sql = Path("app/queries/postgres/products/create_product.sql").read_text()
    assert "product_lineup_id" in sql
