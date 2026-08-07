from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.app.features.tasks.infrastructure.models.task_model import TaskModel
from src.shared.domain.value_objects.entity_id import EntityId


def map_model_to_entity(model: TaskModel) -> TaskEntity:
    """Map a TaskModel (SQLAlchemy) to a TaskEntity (domain)."""
    source_note_id = EntityId(model.source_note_id) if model.source_note_id else None

    return TaskEntity(
        id=EntityId(model.id),
        project_id=EntityId(model.project_id),
        title=model.title,
        description=model.description,
        status=TaskStatus(model.status),
        priority=TaskPriority(model.priority),
        source_note_id=source_note_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
