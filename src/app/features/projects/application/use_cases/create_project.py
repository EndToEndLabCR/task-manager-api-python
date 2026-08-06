from src.app.features.projects.application.dtos.project_dto import (
    ProjectCreateRequest,
    ProjectResponse,
)
from src.app.features.projects.application.dtos.project_dto_mapper import (
    map_create_request_to_entity,
    map_entity_to_response,
)
from src.app.features.projects.application.exceptions.project_exception import (
    ProjectNameAlreadyExistsException,
)
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class CreateProjectUseCase:
    """Use case for creating a new project.

    This use case handles the creation of a project, associating it
    with the requesting user as the owner.
    """

    def __init__(self, project_repository: ProjectRepository):
        self._project_repository = project_repository

    async def execute(self, payload: ProjectCreateRequest, owner_id: str) -> ProjectResponse:
        """Create a new project for the given owner.

        Args:
            payload: The project creation request DTO.
            owner_id: The ID of the user creating the project.

        Returns:
            A ProjectResponse DTO with the created project data.

        Raises:
            ProjectNameAlreadyExistsException: If the owner already has a
                project with the same name.
        """
        project_entity = map_create_request_to_entity(payload, owner_id)

        name_taken = await self._project_repository.exists_by_owner_id_and_name(
            EntityId.from_string(owner_id), project_entity.name
        )
        if name_taken:
            log.warning(
                f"Project name '{project_entity.name}' already exists for owner: {owner_id}"
            )
            raise ProjectNameAlreadyExistsException(project_entity.name)

        saved_project = await self._project_repository.save(project_entity)

        log.info(f"Project created successfully: {saved_project.id} by owner: {owner_id}")

        return map_entity_to_response(saved_project)
