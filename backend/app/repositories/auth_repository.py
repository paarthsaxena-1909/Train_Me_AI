"""SQL-file backed persistence operations for agents and administrators."""

from typing import Any

from sqlalchemy.engine import MappingResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import AccountRecord
from app.repositories.base_repository import BaseRepository


class AuthRepository(BaseRepository):
    @staticmethod
    def _account(result: MappingResult) -> AccountRecord | None:
        row = result.one_or_none()
        return AccountRecord.model_validate(dict(row)) if row is not None else None

    async def create_agent(
        self,
        session: AsyncSession,
        *,
        email: str,
        password_hash: str,
        name: str,
        region: str,
        pincode: str,
    ) -> AccountRecord:
        result = await self.execute_query(
            session,
            "auth",
            "create_agent",
            {
                "email": email,
                "password_hash": password_hash,
                "name": name,
                "region": region,
                "pincode": pincode,
            },
        )
        account = self._account(result.mappings())
        if account is None:
            raise RuntimeError("agent create query returned no account")
        return account

    async def create_admin(
        self,
        session: AsyncSession,
        *,
        email: str,
        password_hash: str,
        name: str,
    ) -> AccountRecord:
        result = await self.execute_query(
            session,
            "auth",
            "create_admin",
            {"email": email, "password_hash": password_hash, "name": name},
        )
        account = self._account(result.mappings())
        if account is None:
            raise RuntimeError("admin create query returned no account")
        return account

    async def get_agent_by_email(self, session: AsyncSession, email: str) -> AccountRecord | None:
        result = await self.execute_query(session, "auth", "get_agent_by_email", {"email": email})
        return self._account(result.mappings())

    async def get_admin_by_email(self, session: AsyncSession, email: str) -> AccountRecord | None:
        result = await self.execute_query(session, "auth", "get_admin_by_email", {"email": email})
        return self._account(result.mappings())

    async def get_agent_by_id(self, session: AsyncSession, account_id: int) -> AccountRecord | None:
        result = await self.execute_query(session, "auth", "get_agent_by_id", {"account_id": account_id})
        return self._account(result.mappings())

    async def get_admin_by_id(self, session: AsyncSession, account_id: int) -> AccountRecord | None:
        result = await self.execute_query(session, "auth", "get_admin_by_id", {"account_id": account_id})
        return self._account(result.mappings())
