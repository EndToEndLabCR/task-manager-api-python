from src.app.features.projects.application.dtos.project_dto import (
    ProjectResponse,
    ProjectUpdateRequest,
)
from src.app.features.projects.application.dtos.project_dto_mapper import map_entity_to_response
from src.app.features.projects.application.exceptions.project_exception import (
    ProjectAccessDeniedException,
    ProjectNameAlreadyExistsException,
    ProjectNotFoundException,
)
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class UpdateProjectUseCase:
    """Use case for updating an existing project.

    This use case validates ownership and applies partial updates
    only to the fields provided in the request.
    """

    def __init__(self, project_repository: ProjectRepository):
        self._project_repository = project_repository

    async def execute(
        self, project_id: str, payload: ProjectUpdateRequest, owner_id: str
    ) -> ProjectResponse:
        """Update a project with partial data, validating ownership.

        Args:
            project_id: The ID of the project to update.
            payload: The update request DTO with optional fields.
            owner_id: The ID of the requesting user.

        Returns:
            A ProjectResponse DTO with the updated project data.

        Raises:
            ProjectNotFoundException: If the project does not exist.
            ProjectAccessDeniedException: If the user does not own the project.
            ProjectNameAlreadyExistsException: If the new name collides with
                another project of the same owner.
        """
        try:
            project_entity_id = EntityId.from_string(project_id)

            project = await self._project_repository.find_by_id(project_entity_id)

            if not project:
                log.warning(f"Project not found for update with ID: {project_id}")
                raise ProjectNotFoundException(project_id)

            if str(project.owner_id) != owner_id:
                log.warning(
                    f"Access denied: user {owner_id} attempted to update project {project_id}"
                )
                raise ProjectAccessDeniedException(project_id, owner_id)

            # Apply partial updates only for provided fields
            if payload.name is not None:
                new_name = payload.name.strip()
                if new_name != project.name:
                    name_taken = await self._project_repository.exists_by_owner_id_and_name(
                        project.owner_id, new_name, exclude_id=project_entity_id
                    )
                    if name_taken:
                        log.warning(
                            f"Project name '{new_name}' already exists for owner: {owner_id}"
                        )
                        raise ProjectNameAlreadyExistsException(new_name)
                project.update_name(new_name)

            if payload.description is not None:
                project.update_description(payload.description.strip())

            if payload.status is not None:
                project.update_status(payload.status)

            if payload.github_repo_url is not None:
                project.update_github_repo_url(payload.github_repo_url.strip() or None)

            updated_project = await self._project_repository.update(project)

            if updated_project is None:
                log.warning(f"Project disappeared during update with ID: {project_id}")
                raise ProjectNotFoundException(project_id)

            log.info(f"Project updated successfully: {project_id} by owner: {owner_id}")

            return map_entity_to_response(updated_project)

        except (
            ValueError,
            ProjectNotFoundException,
            ProjectAccessDeniedException,
            ProjectNameAlreadyExistsException,
        ):
            raise
        except Exception as e:
            log.error(f"Unexpected error in UpdateProjectUseCase: {str(e)}")
            raise
