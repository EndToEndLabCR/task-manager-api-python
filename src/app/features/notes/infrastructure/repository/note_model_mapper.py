from src.app.features.notes.domain.entities.note_entity import NoteEntity
from src.app.features.notes.domain.entities.note_type import NoteType
from src.app.features.notes.infrastructure.models.note_model import NoteModel
from src.shared.domain.value_objects.entity_id import EntityId


def map_model_to_entity(model: NoteModel) -> NoteEntity:
    """Map a NoteModel (SQLAlchemy) to a NoteEntity (domain)."""
    return NoteEntity(
        id=EntityId(model.id),
        project_id=EntityId(model.project_id),
        content=model.content,
        note_type=NoteType(model.note_type),
        is_enriched=model.is_enriched,
        ai_suggestion=model.ai_suggestion,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
