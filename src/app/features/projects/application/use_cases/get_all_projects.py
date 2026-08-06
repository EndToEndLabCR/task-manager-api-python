from src.app.features.projects.application.dtos.project_dto import ProjectListResponse
from src.app.features.projects.application.dtos.project_dto_mapper import map_entity_to_response
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class GetAllProjectsUseCase:
    """Use case for retrieving all projects belonging to a specific owner.

    This use case returns all projects associated with the requesting user.
    """

    def __init__(self, project_repository: ProjectRepository):
        self._project_repository = project_repository

    async def execute(self, owner_id: str) -> ProjectListResponse:
        """Retrieve all projects for the given owner.

        Args:
            owner_id: The ID of the user whose projects to retrieve.

        Returns:
            A ProjectListResponse DTO with the list of projects and total count.
        """
        try:
            owner_entity_id = EntityId.from_string(owner_id)

            projects = await self._project_repository.find_all_by_owner_id(owner_entity_id)

            project_responses = [map_entity_to_response(project) for project in projects]

            log.info(f"Retrieved {len(project_responses)} projects for owner: {owner_id}")

            return ProjectListResponse(
                projects=project_responses,
                total=len(project_responses),
            )

        except ValueError:
            raise
        except Exception as e:
            log.error(f"Unexpected error in GetAllProjectsUseCase: {str(e)}")
            raise
