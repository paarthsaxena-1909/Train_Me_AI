"""Argon2 password hashing used by authentication services."""

from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError


class PasswordService:
    """Small injectable wrapper around pwdlib's recommended Argon2 hasher."""

    def __init__(self, hasher: PasswordHash | None = None) -> None:
        self.hasher = hasher or PasswordHash.recommended()

    def hash(self, password: str) -> str:
        return self.hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return self.hasher.verify(password, password_hash)
        except (ValueError, TypeError, PwdlibError):
            return False


# The alias makes the collaborator's purpose obvious to service callers.
PasswordHasher = PasswordService

_default_service = PasswordService()


def hash_password(password: str) -> str:
    return _default_service.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _default_service.verify(password, password_hash)
