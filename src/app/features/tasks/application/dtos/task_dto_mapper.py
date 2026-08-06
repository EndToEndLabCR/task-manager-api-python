from typing import Optional

from src.app.features.tasks.application.dtos.task_dto import TaskCreateRequest, TaskResponse
from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.shared.domain.value_objects.entity_id import EntityId


def map_entity_to_response(entity: TaskEntity) -> TaskResponse:
    """Convert a TaskEntity to a TaskResponse DTO."""
    return TaskResponse(
        id=str(entity.id),
        project_id=str(entity.project_id),
        title=entity.title,
        description=entity.description,
        status=entity.status,
        priority=entity.priority,
        source_note_id=str(entity.source_note_id) if entity.source_note_id else None,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def map_create_request_to_entity(payload: TaskCreateRequest, project_id: str) -> TaskEntity:
    """Convert a TaskCreateRequest to a TaskEntity."""
    source_note_id: Optional[EntityId] = None
    if payload.source_note_id:
        source_note_id = EntityId.from_string(payload.source_note_id)

    return TaskEntity(
        project_id=EntityId.from_string(project_id),
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        priority=payload.priority or TaskPriority.MEDIUM,
        source_note_id=source_note_id,
    )
