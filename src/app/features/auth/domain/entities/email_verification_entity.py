from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects.entity_id import EntityId


class EmailVerificationEntity(BaseEntity):

    def __init__(
        self,
        id: EntityId,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
        used_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.used_at = used_at
        super().__init__(id, created_at, updated_at)

    @property
    def is_expired(self) -> bool:
        return self.expires_at < datetime.now(timezone.utc)

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        return not self.is_expired and not self.is_used

    def mark_as_used(self) -> None:
        self.used_at = datetime.now(timezone.utc)
        self.mark_as_updated()
