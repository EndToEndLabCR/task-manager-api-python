from abc import ABC, abstractmethod
from typing import Optional

from src.app.features.auth.domain.entities.user_entity import UserEntity
from src.app.features.auth.domain.value_objects.email import Email
from src.shared.domain.value_objects.entity_id import EntityId


class UserRepository(ABC):
    """Contract for user persistence operations."""

    @abstractmethod
    async def save(self, entity: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: EntityId) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def update(self, entity: UserEntity) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        pass
