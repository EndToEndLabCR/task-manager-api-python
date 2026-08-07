# src/app/features/infrastructure/security/jwt_provider.py
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt


class JWTProvider:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self._secret_key = secret_key
        self._algorithm = algorithm

    def create_access_token(self, user_id: str, email: str, expires_hours: int = 24) -> str:
        payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(hours=expires_hours),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: str, email: str, expires_days: int = 7) -> str:
        payload = {
            "sub": user_id,
            "email": email,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def validate_access_token(self, token: str) -> Optional[dict]:
        return self._decode(token, expected_type="access")

    def validate_refresh_token(self, token: str) -> Optional[dict]:
        return self._decode(token, expected_type="refresh")

    def _decode(self, token: str, expected_type: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

            if payload.get("type") != expected_type:
                return None

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None