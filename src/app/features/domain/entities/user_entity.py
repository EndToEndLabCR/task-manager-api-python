from datetime import datetime
from typing import Optional

from src.app.features.domain.value_objects.email import Email
from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects.entity_id import EntityId


class UserEntity(BaseEntity):

    def __init__(self, id: EntityId, email: Email, username: str, password_hash: str,
                 is_verified: bool = False,
                 preferences: Optional[dict] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):

        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.is_verified = is_verified
        self.preferences = preferences or {}
        super().__init__(id, created_at, updated_at)

    def update_password(self, new_password_hash: str) -> None:
        self.password_hash = new_password_hash
        self.mark_as_updated()

    def verify_email(self) -> None:
        self.is_verified = True
        self.mark_as_updated()

    def update_preferences(self, preferences: dict) -> None:
        self.preferences = preferences
        self.mark_as_updated()
