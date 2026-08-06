from abc import ABC, abstractmethod
from typing import List, Optional

from src.app.features.notes.domain.entities.note_entity import NoteEntity
from src.app.features.notes.domain.entities.note_type import NoteType
from src.shared.domain.value_objects.entity_id import EntityId


class NoteRepository(ABC):
    """Abstract contract for note persistence operations."""

    @abstractmethod
    async def save(self, entity: NoteEntity) -> NoteEntity:
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: EntityId) -> Optional[NoteEntity]:
        pass

    @abstractmethod
    async def find_all_by_project_id(
        self,
        project_id: EntityId,
        note_type: Optional[NoteType] = None,
        page: int = 1,
        size: int = 50,
    ) -> List[NoteEntity]:
        pass

    @abstractmethod
    async def count_by_project_id(
        self,
        project_id: EntityId,
        note_type: Optional[NoteType] = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, entity: NoteEntity) -> Optional[NoteEntity]:
        pass

    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        pass
