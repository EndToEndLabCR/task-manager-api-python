from datetime import datetime
from typing import Optional

from src.app.features.notes.domain.entities.note_type import NoteType
from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects.entity_id import EntityId


class NoteEntity(BaseEntity):
    """Domain entity representing a quick note inside a project workspace.

    A note starts as RAW and can be converted to TASK or ARCHITECTURE_DECISION.
    The AI enrichment service can classify it and store a suggestion.
    """

    def __init__(
        self,
        project_id: EntityId,
        content: str,
        note_type: NoteType = NoteType.RAW,
        is_enriched: bool = False,
        ai_suggestion: Optional[dict] = None,
        id: EntityId = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.project_id: EntityId = project_id
        self.content: str = content
        self.note_type: NoteType = note_type
        self.is_enriched: bool = is_enriched
        self.ai_suggestion: Optional[dict] = ai_suggestion

    def update_content(self, content: str) -> None:
        """Update the note content and mark as updated."""
        self.content = content
        self.mark_as_updated()

    def convert_type(self, target_type: NoteType) -> None:
        """Convert the note to a different type and mark as enriched."""
        self.note_type = target_type
        self.is_enriched = True
        self.mark_as_updated()

    def mark_as_enriched(self, ai_suggestion: Optional[dict] = None) -> None:
        """Mark note as enriched by AI and store the suggestion."""
        self.is_enriched = True
        self.ai_suggestion = ai_suggestion
        self.mark_as_updated()
