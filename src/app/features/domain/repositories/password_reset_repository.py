from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.app.features.domain.entities.password_reset_entity import PasswordResetEntity


class PasswordResetRepository(ABC):
    """Contract for password reset token persistence operations."""

    @abstractmethod
    async def save(self, entity: PasswordResetEntity) -> PasswordResetEntity:
        pass

    @abstractmethod
    async def find_by_token_hash(self, token_hash: str) -> Optional[PasswordResetEntity]:
        pass

    @abstractmethod
    async def count_recent_requests(self, user_id: UUID, since: datetime) -> int:
        pass

    @abstractmethod
    async def update(self, entity: PasswordResetEntity) -> Optional[PasswordResetEntity]:
        pass
