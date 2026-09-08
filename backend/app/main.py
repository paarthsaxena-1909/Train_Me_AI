from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers.auth_controller import router as auth_router
from app.controllers.health_controller import router as health_router
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
    for error_type in (AppError, NotFoundError, ConflictError, ForbiddenError, UnauthorizedError):
        application.add_exception_handler(error_type, app_error_handler)
    application.include_router(health_router)
    application.include_router(auth_router)
    return application


app = create_app()
