from abc import ABC, abstractmethod
from typing import Optional, List

from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.shared.domain.value_objects.entity_id import EntityId


class ProjectRepository(ABC):
    """Abstract base class defining the contract for project persistence operations."""

    @abstractmethod
    async def save(self, entity: ProjectEntity) -> ProjectEntity:
        """Persist a new project entity.

        Args:
            entity: The project entity to save.

        Returns:
            The saved project entity.
        """
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: EntityId) -> Optional[ProjectEntity]:
        """Find a project by its unique identifier.

        Args:
            entity_id: The unique identifier of the project.

        Returns:
            The project entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def find_all_by_owner_id(self, owner_id: EntityId) -> List[ProjectEntity]:
        """Find all projects belonging to a specific owner.

        Args:
            owner_id: The unique identifier of the project owner.

        Returns:
            A list of project entities owned by the specified user.
        """
        pass

    @abstractmethod
    async def exists_by_owner_id_and_name(
        self, owner_id: EntityId, name: str, exclude_id: Optional[EntityId] = None
    ) -> bool:
        """Check whether the owner already has a project with the given name.

        Args:
            owner_id: The unique identifier of the project owner.
            name: The project name to check.
            exclude_id: Optional project id to exclude from the check
                (used on updates so a project does not collide with itself).

        Returns:
            True if a project with that name already exists for the owner.
        """
        pass

    @abstractmethod
    async def update(self, entity: ProjectEntity) -> Optional[ProjectEntity]:
        """Update an existing project entity.

        Args:
            entity: The project entity with updated fields.

        Returns:
            The updated project entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        """Delete a project by its unique identifier.

        Args:
            entity_id: The unique identifier of the project to delete.

        Returns:
            True if the project was deleted, False otherwise.
        """
        pass
