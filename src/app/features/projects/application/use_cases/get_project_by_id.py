from src.app.features.projects.application.dtos.project_dto import ProjectResponse
from src.app.features.projects.application.dtos.project_dto_mapper import map_entity_to_response
from src.app.features.projects.application.exceptions.project_exception import (
    ProjectAccessDeniedException,
    ProjectNotFoundException,
)
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class GetProjectByIdUseCase:
    """Use case for retrieving a project by its ID.

    This use case validates that the requesting user is the owner
    of the project before returning the data.
    """

    def __init__(self, project_repository: ProjectRepository):
        self._project_repository = project_repository

    async def execute(self, project_id: str, owner_id: str) -> ProjectResponse:
        """Retrieve a project by ID, validating ownership.

        Args:
            project_id: The ID of the project to retrieve.
            owner_id: The ID of the requesting user.

        Returns:
            A ProjectResponse DTO with the project data.

        Raises:
            ProjectNotFoundException: If the project does not exist.
            ProjectAccessDeniedException: If the user does not own the project.
        """
        try:
            project_entity_id = EntityId.from_string(project_id)

            project = await self._project_repository.find_by_id(project_entity_id)

            if not project:
                log.warning(f"Project not found with ID: {project_id}")
                raise ProjectNotFoundException(project_id)

            if str(project.owner_id) != owner_id:
                log.warning(
                    f"Access denied: user {owner_id} attempted to access project {project_id}"
                )
                raise ProjectAccessDeniedException(project_id, owner_id)

            return map_entity_to_response(project)

        except (ValueError, ProjectNotFoundException, ProjectAccessDeniedException):
            raise
        except Exception as e:
            log.error(f"Unexpected error in GetProjectByIdUseCase: {str(e)}")
            raise
