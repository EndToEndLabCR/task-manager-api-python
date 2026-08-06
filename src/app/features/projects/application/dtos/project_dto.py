from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.app.features.projects.domain.entities.project_status import ProjectStatus


class ProjectCreateRequest(BaseModel):
    """DTO for creating a new project."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[ProjectStatus] = Field(default=ProjectStatus.ACTIVE)
    github_repo_url: Optional[str] = Field(default=None, max_length=255)


class ProjectUpdateRequest(BaseModel):
    """DTO for updating an existing project (partial update)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[ProjectStatus] = Field(default=None)
    github_repo_url: Optional[str] = Field(default=None, max_length=255)


class ProjectResponse(BaseModel):
    """DTO for returning project data in API responses."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: str
    name: str
    description: Optional[str]
    owner_id: str
    status: ProjectStatus
    github_repo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """DTO for returning a list of projects with total count."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    projects: List[ProjectResponse]
    total: int


class DeleteResponse(BaseModel):
    """DTO for confirming project deletion."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    message: str
