from datetime import datetime
from typing import Optional

from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects.entity_id import EntityId


class ProjectEntity(BaseEntity):
    """Domain entity representing a project.

    Attributes:
        id: Unique identifier for the project.
        name: Name of the project.
        description: Description of the project.
        owner_id: EntityId of the user who owns the project.
        status: Current status of the project (ACTIVE, ARCHIVED, COMPLETED).
        github_repo_url: Optional URL of the linked GitHub repository.
        created_at: Timestamp when the project was created.
        updated_at: Timestamp when the project was last updated.
    """

    def __init__(
        self,
        name: str,
        description: str,
        owner_id: EntityId,
        status: ProjectStatus = ProjectStatus.ACTIVE,
        github_repo_url: Optional[str] = None,
        id: EntityId = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.name: str = name
        self.description: str = description
        self.owner_id: EntityId = owner_id
        self.status: ProjectStatus = status
        self.github_repo_url: Optional[str] = github_repo_url

    def update_name(self, name: str) -> None:
        """Update the project name and mark the entity as updated."""
        self.name = name
        self.mark_as_updated()

    def update_description(self, description: str) -> None:
        """Update the project description and mark the entity as updated."""
        self.description = description
        self.mark_as_updated()

    def update_status(self, status: ProjectStatus) -> None:
        """Update the project status and mark the entity as updated."""
        self.status = status
        self.mark_as_updated()

    def update_github_repo_url(self, github_repo_url: Optional[str]) -> None:
        """Update the linked GitHub repository URL and mark the entity as updated."""
        self.github_repo_url = github_repo_url
        self.mark_as_updated()

    def archive(self) -> None:
        """Archive the project by setting its status to ARCHIVED."""
        self.status = ProjectStatus.ARCHIVED
        self.mark_as_updated()
