# src/app/features/infrastructure/security/reset_token_generator.py
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


@dataclass
class ResetToken:
    raw_token: str
    token_hash: str
    expires_at: datetime


class ResetTokenGenerator:

    def __init__(self, expires_hours: int = 1):
        self._expires_hours = expires_hours

    def generate(self) -> ResetToken:
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self._expires_hours)

        return ResetToken(
            raw_token=raw_token,
            token_hash=token_hash,
            expires_at=expires_at,
        )

    def hash(self, raw_token: str) -> str:
        return self._hash(raw_token)

    def _hash(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()