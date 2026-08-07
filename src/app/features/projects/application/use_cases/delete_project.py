from src.app.features.projects.application.dtos.project_dto import DeleteResponse
from src.app.features.projects.application.exceptions.project_exception import (
    ProjectAccessDeniedException,
    ProjectNotFoundException,
)
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class DeleteProjectUseCase:
    """Use case for deleting a project.

    This use case validates that the requesting user owns the project
    before performing the deletion.
    """

    def __init__(self, project_repository: ProjectRepository):
        self._project_repository = project_repository

    async def execute(self, project_id: str, owner_id: str) -> DeleteResponse:
        """Delete a project by ID, validating ownership.

        Args:
            project_id: The ID of the project to delete.
            owner_id: The ID of the requesting user.

        Returns:
            A DeleteResponse DTO confirming the deletion.

        Raises:
            ProjectNotFoundException: If the project does not exist.
            ProjectAccessDeniedException: If the user does not own the project.
        """
        try:
            project_entity_id = EntityId.from_string(project_id)

            project = await self._project_repository.find_by_id(project_entity_id)

            if not project:
                log.warning(f"Project not found for deletion with ID: {project_id}")
                raise ProjectNotFoundException(project_id)

            if str(project.owner_id) != owner_id:
                log.warning(
                    f"Access denied: user {owner_id} attempted to delete project {project_id}"
                )
                raise ProjectAccessDeniedException(project_id, owner_id)

            await self._project_repository.delete(project_entity_id)

            log.info(f"Project deleted successfully: {project_id} by owner: {owner_id}")

            return DeleteResponse(message=f"Project with ID {project_id} deleted successfully")

        except (ValueError, ProjectNotFoundException, ProjectAccessDeniedException):
            raise
        except Exception as e:
            log.error(f"Unexpected error in DeleteProjectUseCase: {str(e)}")
            raise
