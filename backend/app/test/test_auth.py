from __future__ import annotations

import importlib
import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import httpx
import jwt
import pytest

from app.errors import ForbiddenError
from app.main import create_app
from app.models.auth import AccountRecord, Principal
from app.repositories.auth_repository import AuthRepository
from app.security.dependencies import require_admin, require_agent
from app.security.passwords import PasswordService
from app.security.tokens import TokenService
from app.services.auth_service import AuthService
from app.settings import Settings
from database.models import Agent


class FakeSession:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


class FakeAuthRepository:
    def __init__(self) -> None:
        self.agents: dict[int, AccountRecord] = {}
        self.admins: dict[int, AccountRecord] = {}
        self.next_id = 1
        self.create_agent_inputs: list[dict[str, Any]] = []

    async def get_agent_by_email(self, session: Any, email: str) -> AccountRecord | None:
        return next((account for account in self.agents.values() if account.email == email), None)

    async def get_admin_by_email(self, session: Any, email: str) -> AccountRecord | None:
        return next((account for account in self.admins.values() if account.email == email), None)

    async def get_agent_by_id(self, session: Any, account_id: int) -> AccountRecord | None:
        return self.agents.get(account_id)

    async def get_admin_by_id(self, session: Any, account_id: int) -> AccountRecord | None:
        return self.admins.get(account_id)

    async def create_agent(self, session: Any, **values: Any) -> AccountRecord:
        self.create_agent_inputs.append(values)
        account = AccountRecord(id=self.next_id, role="agent", **values)
        self.next_id += 1
        self.agents[account.id] = account
        return account

    async def create_admin(self, session: Any, **values: Any) -> AccountRecord:
        account = AccountRecord(id=self.next_id, role="admin", **values)
        self.next_id += 1
        self.admins[account.id] = account
        return account


class ASGIClient:
    def __init__(self, application: Any) -> None:
        self.application = application

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        async def send() -> httpx.Response:
            transport = httpx.ASGITransport(app=self.application)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                return await client.request(method, path, **kwargs)

        return asyncio.run(send())

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", path, **kwargs)

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", path, **kwargs)


def build_client(repository: FakeAuthRepository | None = None) -> tuple[ASGIClient, FakeAuthRepository, FakeSession]:
    repository = repository or FakeAuthRepository()
    session = FakeSession()
    application = create_app()
    from app.controllers.auth_controller import get_auth_service
    from app.db.session import get_db_session
    from app.security.dependencies import get_auth_repository

    async def override_auth_service() -> AuthService:
        return AuthService(
            repository=repository,
            passwords=PasswordService(),
            tokens=TokenService(Settings(jwt_secret="test-secret", jwt_algorithm="HS256", access_token_minutes=60)),
        )

    async def override_auth_repository() -> FakeAuthRepository:
        return repository

    from app.security.dependencies import get_token_service

    async def override_token_service() -> TokenService:
        return TokenService(Settings(jwt_secret="test-secret", jwt_algorithm="HS256", access_token_minutes=60))

    application.dependency_overrides[get_auth_service] = override_auth_service
    application.dependency_overrides[get_auth_repository] = override_auth_repository
    application.dependency_overrides[get_token_service] = override_token_service

    async def override_session():
        yield session

    application.dependency_overrides[get_db_session] = override_session
    return ASGIClient(application), repository, session


def test_agent_signup_preserves_leading_zero_pincode_and_hashes_password() -> None:
    client, repository, session = build_client()

    response = client.post(
        "/api/v1/auth/agents/signup",
        json={
            "email": " Agent@Example.COM ",
            "password": "S3cret-password",
            "name": "Asha",
            "pincode": "012345",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "agent@example.com"
    saved = repository.agents[1]
    assert saved.pincode == "012345"
    assert saved.password_hash != "S3cret-password"
    assert PasswordService().verify("S3cret-password", saved.password_hash)
    assert repository.create_agent_inputs[0]["email"] == "agent@example.com"
    assert session.commits == 1


def test_admin_signup_is_public_and_normalizes_email() -> None:
    client, repository, _ = build_client()

    response = client.post(
        "/api/v1/auth/admins/signup",
        json={"email": " Admin@Example.COM ", "password": "S3cret-password", "name": "Mira"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "admin"
    assert repository.admins[1].email == "admin@example.com"
    assert repository.admins[1].password_hash.startswith("$argon2")


@pytest.mark.parametrize("pincode", ["12345", "1234567", "12A345", 12345])
def test_agent_signup_rejects_non_six_digit_pincode(pincode: object) -> None:
    client, _, _ = build_client()

    response = client.post(
        "/api/v1/auth/agents/signup",
        json={"email": "agent@example.com", "password": "S3cret-password", "name": "Asha", "pincode": pincode},
    )

    assert response.status_code == 422


def test_duplicate_email_returns_conflict_without_committing() -> None:
    repository = FakeAuthRepository()
    repository.agents[1] = AccountRecord(
        id=1,
        role="agent",
        email="agent@example.com",
        password_hash=PasswordService().hash("S3cret-password"),
        name="Existing",
        region="",
        pincode="012345",
    )
    client, _, session = build_client(repository)

    response = client.post(
        "/api/v1/auth/agents/signup",
        json={
            "email": "AGENT@example.com",
            "password": "S3cret-password",
            "name": "Asha",
            "pincode": "012345",
        },
    )

    assert response.status_code == 409
    assert session.commits == 0
    assert session.rollbacks == 1


def test_login_issues_real_expiring_jwt_with_role_claims() -> None:
    repository = FakeAuthRepository()
    repository.agents[1] = AccountRecord(
        id=1,
        role="agent",
        email="agent@example.com",
        password_hash=PasswordService().hash("S3cret-password"),
        name="Asha",
        region="",
        pincode="012345",
    )
    client, _, _ = build_client(repository)

    response = client.post(
        "/api/v1/auth/agents/login",
        json={"email": "AGENT@example.com", "password": "S3cret-password"},
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    claims = jwt.decode(token, "test-secret", algorithms=["HS256"])
    assert claims["sub"] == "1"
    assert claims["role"] == "agent"
    assert "iat" in claims and "exp" in claims


def test_incorrect_credentials_return_unauthorized() -> None:
    repository = FakeAuthRepository()
    repository.admins[1] = AccountRecord(
        id=1,
        role="admin",
        email="admin@example.com",
        password_hash=PasswordService().hash("correct-password"),
        name="Mira",
    )
    client, _, _ = build_client(repository)

    response = client.post(
        "/api/v1/auth/admins/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_malformed_stored_hash_is_treated_as_incorrect_credentials() -> None:
    repository = FakeAuthRepository()
    repository.agents[1] = AccountRecord(
        id=1,
        role="agent",
        email="agent@example.com",
        password_hash="not-an-argon2-hash",
        name="Asha",
        region="",
        pincode="012345",
    )
    client, _, _ = build_client(repository)

    response = client.post(
        "/api/v1/auth/agents/login",
        json={"email": "agent@example.com", "password": "S3cret-password"},
    )

    assert response.status_code == 401


def test_expired_and_wrong_algorithm_tokens_are_rejected() -> None:
    settings = Settings(jwt_secret="test-secret", jwt_algorithm="HS256", access_token_minutes=60)
    service = TokenService(settings)
    expired = jwt.encode(
        {"sub": "1", "role": "agent", "iat": datetime.now(UTC) - timedelta(minutes=5), "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    wrong_algorithm = jwt.encode(
        {"sub": "1", "role": "agent", "iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.jwt_secret,
        algorithm="HS512",
    )

    with pytest.raises(ValueError):
        service.decode(expired)
    with pytest.raises(ValueError):
        service.decode(wrong_algorithm)


def test_me_rechecks_active_account_and_rejects_deleted_account() -> None:
    repository = FakeAuthRepository()
    repository.agents[1] = AccountRecord(
        id=1,
        role="agent",
        email="agent@example.com",
        password_hash=PasswordService().hash("S3cret-password"),
        name="Asha",
        region="",
        pincode="012345",
    )
    client, _, _ = build_client(repository)
    token = TokenService(Settings(jwt_secret="test-secret", jwt_algorithm="HS256", access_token_minutes=60)).create(
        Principal(account_id=1, role="agent")
    )

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "agent@example.com"

    repository.agents.clear()
    deleted_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert deleted_response.status_code == 401


def test_me_preserves_an_uncaptured_legacy_pincode_as_null() -> None:
    repository = FakeAuthRepository()
    repository.agents[1] = AccountRecord(
        id=1,
        role="agent",
        email="legacy@example.com",
        password_hash=PasswordService().hash("S3cret-password"),
        name="Legacy",
        region="",
        pincode=None,
    )
    client, _, _ = build_client(repository)
    token = TokenService(Settings(jwt_secret="test-secret", jwt_algorithm="HS256", access_token_minutes=60)).create(
        Principal(account_id=1, role="agent")
    )

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["pincode"] is None


def test_me_rejects_a_soft_deleted_record_even_if_repository_returns_it() -> None:
    repository = FakeAuthRepository()
    repository.agents[1] = AccountRecord(
        id=1,
        role="agent",
        email="agent@example.com",
        password_hash=PasswordService().hash("S3cret-password"),
        name="Asha",
        region="",
        pincode="012345",
        deleted_at=datetime.now(UTC),
    )
    client, _, _ = build_client(repository)
    token = TokenService(Settings(jwt_secret="test-secret", jwt_algorithm="HS256", access_token_minutes=60)).create(
        Principal(account_id=1, role="agent")
    )

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_role_dependencies_deny_the_other_role() -> None:
    with pytest.raises(ForbiddenError):
        require_admin(Principal(account_id=1, role="agent"))
    with pytest.raises(ForbiddenError):
        require_agent(Principal(account_id=1, role="admin"))


def test_auth_migration_renames_passwords_and_adds_agent_pincode(monkeypatch: pytest.MonkeyPatch) -> None:
    migration = importlib.import_module("database.versions.0002_authentication")
    operations: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    for name in ("alter_column", "add_column", "drop_column", "create_check_constraint", "drop_constraint"):
        monkeypatch.setattr(
            migration.op,
            name,
            lambda *args, _name=name, **kwargs: operations.append((_name, args, kwargs)),
        )

    migration.upgrade()

    renames = {
        args[:2]: kwargs["new_column_name"]
        for name, args, kwargs in operations
        if name == "alter_column" and "new_column_name" in kwargs
    }
    assert renames[("agents", "password")] == "password_hash"
    assert renames[("admins", "password")] == "password_hash"
    added = [args for name, args, _ in operations if name == "add_column"]
    assert added and added[0][0] == "agents" and added[0][1].name == "pincode"
    pincode_column = added[0][1]
    assert pincode_column.nullable is True
    assert pincode_column.server_default is None
    checks = [args for name, args, _ in operations if name == "create_check_constraint"]
    assert checks and checks[0][:2] == ("ck_agents_pincode_six_digits", "agents")
    assert "[0-9]{6}" in str(checks[0][2])


def test_agent_pincode_is_nullable_and_database_checked() -> None:
    pincode = Agent.__table__.c.pincode

    assert pincode.nullable is True
    assert pincode.type.length == 6
    checks = [constraint for constraint in Agent.__table__.constraints if constraint.name == "ck_agents_pincode_six_digits"]
    assert len(checks) == 1
    assert "[0-9]{6}" in str(checks[0].sqltext)


def test_non_development_settings_reject_default_or_short_jwt_secrets() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(environment="production", jwt_secret="development-secret-change-me")
    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(environment="staging", jwt_secret="too-short")


def test_token_service_rejects_unsafe_non_development_configuration() -> None:
    unsafe_settings = SimpleNamespace(
        environment="production",
        jwt_secret="unsafe",
        jwt_algorithm="HS256",
        access_token_minutes=60,
    )

    with pytest.raises(ValueError, match="JWT_SECRET"):
        TokenService(unsafe_settings)  # type: ignore[arg-type]


def test_development_and_test_settings_accept_development_secret() -> None:
    for environment in ("development", "test"):
        settings = Settings(environment=environment, jwt_secret="development-secret-change-me")
        token_service = TokenService(settings)
        token = token_service.create(Principal(account_id=3, role="agent"))
        assert token_service.decode(token) == Principal(account_id=3, role="agent")


def test_production_settings_accept_a_strong_jwt_secret() -> None:
    settings = Settings(environment="production", jwt_secret="s" * 32)
    token_service = TokenService(settings)
    token = token_service.create(Principal(account_id=4, role="admin"))

    assert token_service.decode(token) == Principal(account_id=4, role="admin")


def test_auth_repository_loads_each_operation_from_postgres_sql_files() -> None:
    repository = AuthRepository()
    for query_name in (
        "create_agent",
        "create_admin",
        "get_agent_by_email",
        "get_admin_by_email",
        "get_agent_by_id",
        "get_admin_by_id",
    ):
        sql = repository.load_query("auth", query_name)
        assert sql
        assert "deletedAt" in sql or query_name.startswith("create_")
