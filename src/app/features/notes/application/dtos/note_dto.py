from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from src.app.features.notes.domain.entities.note_type import NoteType


class NoteCreateRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    content: str = Field(..., min_length=1, max_length=5000)


class NoteUpdateRequest(BaseModel):
    """Partial update of a note's content.

    Changing note_type is intentionally not allowed here — type changes
    must go through the convert endpoint so conversion rules apply.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    content: Optional[str] = Field(default=None, min_length=1, max_length=5000)


class NoteConvertRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    target_type: NoteType

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, value: NoteType) -> NoteType:
        if value == NoteType.RAW:
            raise ValueError("target_type must be 'task' or 'architecture_decision'")
        return value


class NoteResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: str
    project_id: str
    content: str
    note_type: NoteType
    is_enriched: bool
    ai_suggestion: Optional[dict]
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: List[NoteResponse]
    total: int
    page: int
    size: int


class NoteConvertResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    message: str
    created_task_id: Optional[str] = None
