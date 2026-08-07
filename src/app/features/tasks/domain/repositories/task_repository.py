from abc import ABC, abstractmethod
from typing import List, Optional

from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.shared.domain.value_objects.entity_id import EntityId


class TaskRepository(ABC):
    """Abstract contract for task persistence operations."""

    @abstractmethod
    async def save(self, entity: TaskEntity) -> TaskEntity:
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: EntityId) -> Optional[TaskEntity]:
        pass

    @abstractmethod
    async def find_all_by_project_id(
        self,
        project_id: EntityId,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        page: int = 1,
        size: int = 50,
    ) -> List[TaskEntity]:
        pass

    @abstractmethod
    async def count_by_project_id(
        self,
        project_id: EntityId,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> int:
        pass

    @abstractmethod
    async def update(self, entity: TaskEntity) -> Optional[TaskEntity]:
        pass

    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        pass
