from sqlalchemy import Boolean, Column, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.shared.infrastructure.models.base_model import BaseModel


class NoteModel(BaseModel):
    """SQLAlchemy model for the 'notes' table."""

    __tablename__ = "notes"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    note_type = Column(String(30), nullable=False, default="raw", server_default="raw")
    is_enriched = Column(Boolean, nullable=False, default=False, server_default="false")
    ai_suggestion = Column(JSON, nullable=True)
