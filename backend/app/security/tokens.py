"""Signed, expiring JWT access tokens with an explicitly pinned algorithm."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError

from app.models.auth import Principal
from app.settings import (
    DEFAULT_JWT_SECRET,
    DEVELOPMENT_ENVIRONMENTS,
    MIN_JWT_SECRET_LENGTH,
    Settings,
    get_settings,
)


def _validate_secret(environment: str, secret: str) -> None:
    if environment.strip().lower() not in DEVELOPMENT_ENVIRONMENTS and (
        secret == DEFAULT_JWT_SECRET or len(secret) < MIN_JWT_SECRET_LENGTH
    ):
        raise ValueError(
            "JWT_SECRET must be at least 32 characters and must be overridden outside development/test"
        )


class TokenService:
    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.access_token_minutes = settings.access_token_minutes
        _validate_secret(settings.environment, self.secret)

    def create(self, principal: Principal, expires_delta: timedelta | None = None) -> str:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + (expires_delta or timedelta(minutes=self.access_token_minutes))
        payload: dict[str, Any] = {
            "sub": str(principal.account_id),
            "role": principal.role,
            "iat": issued_at,
            "exp": expires_at,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode(self, token: str) -> Principal:
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"require": ["sub", "role", "iat", "exp"]},
            )
            account_id = int(payload["sub"])
            role = payload["role"]
            return Principal(account_id=account_id, role=role)
        except (InvalidTokenError, KeyError, TypeError, ValueError) as error:
            raise ValueError("invalid or expired access token") from error


def create_access_token(principal: Principal, settings: Settings | None = None) -> str:
    return TokenService(settings).create(principal)


def decode_access_token(token: str, settings: Settings | None = None) -> Principal:
    return TokenService(settings).decode(token)
