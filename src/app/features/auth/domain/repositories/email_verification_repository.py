from abc import ABC, abstractmethod
from typing import Optional

from src.app.features.auth.domain.entities.email_verification_entity import EmailVerificationEntity


class EmailVerificationRepository(ABC):
    """Contract for email verification token persistence operations."""

    @abstractmethod
    async def save(self, entity: EmailVerificationEntity) -> EmailVerificationEntity:
        pass

    @abstractmethod
    async def find_by_token_hash(self, token_hash: str) -> Optional[EmailVerificationEntity]:
        pass

    @abstractmethod
    async def update(self, entity: EmailVerificationEntity) -> Optional[EmailVerificationEntity]:
        pass
