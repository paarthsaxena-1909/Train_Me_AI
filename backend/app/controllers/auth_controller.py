"""HTTP routes for role-explicit authentication."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.session import DbSession
from app.models.auth import (
    AccountResponse,
    AdminSignupRequest,
    AgentSignupRequest,
    LoginRequest,
    TokenResponse,
)
from app.repositories.auth_repository import AuthRepository
from app.security.dependencies import CurrentPrincipal, get_current_principal
from app.services.auth_service import AuthService


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


async def get_auth_service() -> AuthService:
    return AuthService(repository=AuthRepository())


AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/agents/signup", response_model=AccountResponse, status_code=201)
async def agent_signup(
    payload: AgentSignupRequest,
    session: DbSession,
    service: AuthServiceDependency,
) -> AccountResponse:
    return await service.signup_agent(session, payload)


@router.post("/agents/login", response_model=TokenResponse)
async def agent_login(
    payload: LoginRequest,
    session: DbSession,
    service: AuthServiceDependency,
) -> TokenResponse:
    return await service.login_agent(session, payload)


@router.post("/admins/signup", response_model=AccountResponse, status_code=201)
async def admin_signup(
    payload: AdminSignupRequest,
    session: DbSession,
    service: AuthServiceDependency,
) -> AccountResponse:
    return await service.signup_admin(session, payload)


@router.post("/admins/login", response_model=TokenResponse)
async def admin_login(
    payload: LoginRequest,
    session: DbSession,
    service: AuthServiceDependency,
) -> TokenResponse:
    return await service.login_admin(session, payload)


@router.get("/me", response_model=AccountResponse)
async def current_account(
    session: DbSession,
    principal: CurrentPrincipal,
    service: AuthServiceDependency,
) -> AccountResponse:
    return await service.get_current_account(session, principal)


__all__ = ["get_auth_service", "get_current_principal", "router"]
