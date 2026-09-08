from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.session import DbSession
from app.models.products import ProductCreate, ProductResponse, VariantCreate, VariantResponse
from app.security.dependencies import CurrentAdmin, CurrentPrincipal
from app.services.products_service import ProductsService

router = APIRouter(prefix="/api/v1/products", tags=["products"])


async def get_products_service() -> ProductsService:
    return ProductsService()


ServiceDependency = Annotated[ProductsService, Depends(get_products_service)]


@router.get("", response_model=list[ProductResponse])
async def list_products(
    session: DbSession,
    _: CurrentPrincipal,
    service: ServiceDependency,
) -> list[ProductResponse]:
    return await service.list(session)


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreate,
    session: DbSession,
    _: CurrentAdmin,
    service: ServiceDependency,
) -> ProductResponse:
    return await service.create(session, payload)


@router.post("/{product_id}/variants", response_model=VariantResponse, status_code=201)
async def create_variant(
    product_id: int,
    payload: VariantCreate,
    session: DbSession,
    _: CurrentAdmin,
    service: ServiceDependency,
) -> VariantResponse:
    return await service.add_variant(session, product_id, payload)
