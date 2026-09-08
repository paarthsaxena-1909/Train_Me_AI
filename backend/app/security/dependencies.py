"""FastAPI dependencies for bearer-token validation and role enforcement."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.db.session import DbSession
from app.errors import ForbiddenError, UnauthorizedError
from app.logger import AppLogger
from app.models.auth import Principal
from app.repositories.auth_repository import AuthRepository
from app.security.tokens import TokenService


bearer_scheme = HTTPBearer(auto_error=False)
logger = AppLogger.get_logger(__name__)


async def get_auth_repository() -> AuthRepository:
    return AuthRepository()


async def get_token_service() -> TokenService:
    return TokenService()


AuthRepositoryDependency = Annotated[AuthRepository, Depends(get_auth_repository)]
TokenServiceDependency = Annotated[TokenService, Depends(get_token_service)]


async def get_current_principal(
    session: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    repository: AuthRepositoryDependency,
    tokens: TokenServiceDependency,
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        logger.warning("authentication rejected: bearer token required")
        raise UnauthorizedError("A bearer token is required")
    try:
        principal = tokens.decode(credentials.credentials)
    except ValueError as error:
        logger.warning("authentication rejected: invalid or expired token")
        raise UnauthorizedError("Invalid or expired access token") from error

    finder = repository.get_agent_by_id if principal.role == "agent" else repository.get_admin_by_id
    account = await finder(session, principal.account_id)
    if account is None or account.deleted_at is not None:
        logger.warning("authentication rejected: inactive account")
        raise UnauthorizedError("Account is no longer active")
    logger.debug("authentication succeeded: account_id=%s role=%s", principal.account_id, principal.role)
    return principal


CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]


def require_agent(principal: CurrentPrincipal) -> Principal:
    if principal.role != "agent":
        logger.warning(
            "authorization rejected: account_id=%s current_role=%s required_role=agent",
            principal.account_id,
            principal.role,
        )
        raise ForbiddenError("Agent role required")
    return principal


def require_admin(principal: CurrentPrincipal) -> Principal:
    if principal.role != "admin":
        logger.warning(
            "authorization rejected: account_id=%s current_role=%s required_role=admin",
            principal.account_id,
            principal.role,
        )
        raise ForbiddenError("Administrator role required")
    return principal


CurrentAgent = Annotated[Principal, Depends(require_agent)]
CurrentAdmin = Annotated[Principal, Depends(require_admin)]


__all__ = [
    "CurrentAdmin",
    "CurrentAgent",
    "CurrentPrincipal",
    "get_auth_repository",
    "get_current_principal",
    "get_token_service",
    "require_admin",
    "require_agent",
]
