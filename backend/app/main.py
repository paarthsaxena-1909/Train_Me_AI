from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers.auth_controller import router as auth_router
from app.controllers.health_controller import router as health_router
from app.controllers.products_controller import router as products_router, lineups_router
from app.controllers.qa_controller import router as qa_router
from app.controllers.assignments_controller import router as assignments_router
from app.controllers.evaluations_controller import router as evaluations_router
from app.errors import AppError, ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.logger import AppLogger
from app.settings import get_settings


logger = AppLogger.get_logger(__name__)


async def app_error_handler(request: Request, error: AppError) -> JSONResponse:
    """Return one stable error shape for expected application failures."""
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


def create_app() -> FastAPI:
    settings = get_settings()
    AppLogger.configure(settings.log_level)
    application = FastAPI(title=settings.app_name)
    logger.info("application created")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def log_rejected_cors_preflight(request: Request, call_next):
        response = await call_next(request)
        origin = request.headers.get("origin")
        requested_method = request.headers.get("access-control-request-method")
        if request.method == "OPTIONS" and origin and requested_method and response.status_code >= 400:
            reason = "origin_not_allowed" if origin not in settings.cors_origin_list else "preflight_rejected"
            logger.warning(
                "cors preflight rejected reason=%s origin=%s requested_method=%s requested_headers=%s allowed_origins=%s status_code=%s",
                reason,
                origin,
                requested_method,
                request.headers.get("access-control-request-headers", ""),
                ",".join(settings.cors_origin_list),
                response.status_code,
            )
        return response

    for error_type in (AppError, NotFoundError, ConflictError, ForbiddenError, UnauthorizedError):
        application.add_exception_handler(error_type, app_error_handler)
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(products_router)
    application.include_router(lineups_router)
    application.include_router(qa_router)
    application.include_router(assignments_router)
    application.include_router(evaluations_router)
    return application


app = create_app()
