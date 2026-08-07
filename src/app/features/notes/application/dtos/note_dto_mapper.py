from src.app.features.notes.application.dtos.note_dto import NoteCreateRequest, NoteResponse
from src.app.features.notes.domain.entities.note_entity import NoteEntity
from src.shared.domain.value_objects.entity_id import EntityId


def map_entity_to_response(entity: NoteEntity) -> NoteResponse:
    """Convert a NoteEntity to a NoteResponse DTO."""
    return NoteResponse(
        id=str(entity.id),
        project_id=str(entity.project_id),
        content=entity.content,
        note_type=entity.note_type,
        is_enriched=entity.is_enriched,
        ai_suggestion=entity.ai_suggestion,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def map_create_request_to_entity(payload: NoteCreateRequest, project_id: str) -> NoteEntity:
    """Convert a NoteCreateRequest and project_id string to a NoteEntity."""
    return NoteEntity(
        project_id=EntityId.from_string(project_id),
        content=payload.content.strip(),
    )
