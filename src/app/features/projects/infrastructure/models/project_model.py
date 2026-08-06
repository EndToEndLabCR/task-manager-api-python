from sqlalchemy import Column, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from src.shared.infrastructure.models.base_model import BaseModel


class ProjectModel(BaseModel):
    """SQLAlchemy model for the 'projects' table."""

    __tablename__ = 'projects'
    __table_args__ = (
        UniqueConstraint('owner_id', 'name', name='uq_projects_owner_id_name'),
    )

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(String(20), nullable=False, default='active', server_default='active')
    github_repo_url = Column(String(255), nullable=True)
