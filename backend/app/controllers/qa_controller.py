from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.session import DbSession
from app.models.qa import QueryCreate, QueryResponse
from app.orchestration.product_context import ProductContextAdapter
from app.security.dependencies import CurrentAgent
from app.services.qa_service import QAService
from app.services.products_service import ProductsService


router = APIRouter(prefix="/api/v1/queries", tags=["qa"])


async def get_qa_service(session: DbSession) -> QAService:
    return QAService(product_context=ProductContextAdapter(session, ProductsService()))


ServiceDependency = Annotated[QAService, Depends(get_qa_service)]


@router.post("", response_model=QueryResponse, status_code=201)
async def ask_query(
    payload: QueryCreate,
    session: DbSession,
    _: CurrentAgent,
    service: ServiceDependency,
) -> QueryResponse:
    return await service.ask(session, payload)
