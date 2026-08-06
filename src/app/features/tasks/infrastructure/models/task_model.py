from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.shared.infrastructure.models.base_model import BaseModel


class TaskModel(BaseModel):
    """SQLAlchemy model for the 'tasks' table."""

    __tablename__ = "tasks"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="todo", server_default="todo")
    priority = Column(String(20), nullable=False, default="medium", server_default="medium")
    source_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="SET NULL"), nullable=True)
