"""Authentication business rules and transaction boundaries."""

from typing import Protocol

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import ConflictError, UnauthorizedError
from app.logger import AppLogger
from app.models.auth import (
    AccountRecord,
    AccountResponse,
    AdminSignupRequest,
    AgentSignupRequest,
    LoginRequest,
    Principal,
    Role,
    TokenResponse,
)
from app.repositories.auth_repository import AuthRepository
from app.security.passwords import PasswordService
from app.security.tokens import TokenService


logger = AppLogger.get_logger(__name__)


class AuthRepositoryPort(Protocol):
    async def create_agent(
        self,
        session: AsyncSession,
        *,
        email: str,
        password_hash: str,
        name: str,
        region: str,
        pincode: str,
    ) -> AccountRecord: ...

    async def create_admin(
        self,
        session: AsyncSession,
        *,
        email: str,
        password_hash: str,
        name: str,
    ) -> AccountRecord: ...

    async def get_agent_by_email(self, session: AsyncSession, email: str) -> AccountRecord | None: ...

    async def get_admin_by_email(self, session: AsyncSession, email: str) -> AccountRecord | None: ...

    async def get_agent_by_id(self, session: AsyncSession, account_id: int) -> AccountRecord | None: ...

    async def get_admin_by_id(self, session: AsyncSession, account_id: int) -> AccountRecord | None: ...


class AuthService:
    """Coordinate password hashing, persistence, and token issuance."""

    def __init__(
        self,
        repository: AuthRepositoryPort | None = None,
        passwords: PasswordService | None = None,
        tokens: TokenService | None = None,
        *,
        password_service: PasswordService | None = None,
        token_service: TokenService | None = None,
    ) -> None:
        self.repository = repository or AuthRepository()
        self.passwords = passwords or password_service or PasswordService()
        self.tokens = tokens or token_service or TokenService()

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _public_account(account: AccountRecord) -> AccountResponse:
        return AccountResponse.model_validate(account)

    async def signup_agent(self, session: AsyncSession, payload: AgentSignupRequest) -> AccountResponse:
        email = self._normalize_email(payload.email)
        if await self.repository.get_agent_by_email(session, email) is not None:
            await session.rollback()
            logger.warning("agent signup rejected: duplicate account")
            raise ConflictError("An agent with this email already exists")
        try:
            account = await self.repository.create_agent(
                session,
                email=email,
                password_hash=self.passwords.hash(payload.password),
                name=payload.name.strip(),
                region=payload.region.strip(),
                pincode=payload.pincode,
            )
            await session.commit()
        except IntegrityError as error:
            await session.rollback()
            raise ConflictError("An agent with this email already exists") from error
        except Exception:
            await session.rollback()
            raise
        logger.info("agent account created: account_id=%s", account.id)
        return self._public_account(account)

    async def signup_admin(self, session: AsyncSession, payload: AdminSignupRequest) -> AccountResponse:
        email = self._normalize_email(payload.email)
        if await self.repository.get_admin_by_email(session, email) is not None:
            await session.rollback()
            logger.warning("admin signup rejected: duplicate account")
            raise ConflictError("An administrator with this email already exists")
        try:
            account = await self.repository.create_admin(
                session,
                email=email,
                password_hash=self.passwords.hash(payload.password),
                name=payload.name.strip(),
            )
            await session.commit()
        except IntegrityError as error:
            await session.rollback()
            raise ConflictError("An administrator with this email already exists") from error
        except Exception:
            await session.rollback()
            raise
        logger.info("admin account created: account_id=%s", account.id)
        return self._public_account(account)

    async def login_agent(self, session: AsyncSession, payload: LoginRequest) -> TokenResponse:
        return await self._login(session, payload, role="agent")

    async def login_admin(self, session: AsyncSession, payload: LoginRequest) -> TokenResponse:
        return await self._login(session, payload, role="admin")

    async def _login(self, session: AsyncSession, payload: LoginRequest, *, role: Role) -> TokenResponse:
        email = self._normalize_email(payload.email)
        finder = (
            self.repository.get_agent_by_email if role == "agent" else self.repository.get_admin_by_email
        )
        account = await finder(session, email)
        if account is None or not self.passwords.verify(payload.password, account.password_hash):
            logger.warning("%s login rejected: invalid credentials", role)
            raise UnauthorizedError("Incorrect email or password")
        principal = Principal(account_id=account.id, role=role)
        logger.info("%s login succeeded: account_id=%s", role, account.id)
        return TokenResponse(access_token=self.tokens.create(principal), account=self._public_account(account))

    async def get_current_account(self, session: AsyncSession, principal: Principal) -> AccountResponse:
        finder = self.repository.get_agent_by_id if principal.role == "agent" else self.repository.get_admin_by_id
        account = await finder(session, principal.account_id)
        if account is None or account.deleted_at is not None:
            logger.warning("current account rejected: inactive account")
            raise UnauthorizedError("Account is no longer active")
        return self._public_account(account)

    # Descriptive aliases keep the service easy to discover for callers.
    register_agent = signup_agent
    register_admin = signup_admin
    authenticate_agent = login_agent
    authenticate_admin = login_admin
