from datetime import datetime
from typing import Optional

from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects.entity_id import EntityId


class TaskEntity(BaseEntity):
    """Domain entity representing a lightweight task inside a project workspace.

    Tasks can originate from a note conversion (source_note_id) or be
    created directly. They follow a simple TODO → IN_PROGRESS → DONE lifecycle.
    """

    def __init__(
        self,
        project_id: EntityId,
        title: str,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.TODO,
        priority: TaskPriority = TaskPriority.MEDIUM,
        source_note_id: Optional[EntityId] = None,
        id: EntityId = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.project_id: EntityId = project_id
        self.title: str = title
        self.description: Optional[str] = description
        self.status: TaskStatus = status
        self.priority: TaskPriority = priority
        self.source_note_id: Optional[EntityId] = source_note_id

    def update_title(self, title: str) -> None:
        """Update the task title."""
        self.title = title
        self.mark_as_updated()

    def update_description(self, description: Optional[str]) -> None:
        """Update the task description."""
        self.description = description
        self.mark_as_updated()

    def update_status(self, status: TaskStatus) -> None:
        """Transition the task to a new status."""
        self.status = status
        self.mark_as_updated()

    def update_priority(self, priority: TaskPriority) -> None:
        """Update the task priority."""
        self.priority = priority
        self.mark_as_updated()
