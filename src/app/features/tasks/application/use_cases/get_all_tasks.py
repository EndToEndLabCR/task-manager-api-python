from typing import Optional

from src.app.features.tasks.application.dtos.task_dto import TaskListResponse
from src.app.features.tasks.application.dtos.task_dto_mapper import map_entity_to_response
from src.app.features.tasks.application.exceptions.task_exception import TaskAccessDeniedException
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.app.features.tasks.domain.repositories.task_repository import TaskRepository
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class GetAllTasksUseCase:
    """Retrieve paginated tasks for a project, optionally filtered by status and/or priority."""

    def __init__(self, task_repository: TaskRepository, project_repository: ProjectRepository):
        self._task_repository = task_repository
        self._project_repository = project_repository

    async def execute(
        self,
        project_id: str,
        owner_id: str,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        page: int = 1,
        size: int = 50,
    ) -> TaskListResponse:
        project = await self._project_repository.find_by_id(EntityId.from_string(project_id))

        if not project:
            raise TaskAccessDeniedException(project_id, owner_id)

        if str(project.owner_id) != owner_id:
            raise TaskAccessDeniedException(project_id, owner_id)

        project_entity_id = EntityId.from_string(project_id)
        tasks = await self._task_repository.find_all_by_project_id(project_entity_id, status, priority, page, size)
        total = await self._task_repository.count_by_project_id(project_entity_id, status, priority)

        log.info(f"Retrieved {len(tasks)} tasks for project: {project_id}")
        return TaskListResponse(
            items=[map_entity_to_response(t) for t in tasks],
            total=total,
            page=page,
            size=size,
        )
