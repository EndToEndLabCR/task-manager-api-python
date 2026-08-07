from src.app.features.tasks.application.dtos.task_dto import TaskResponse, TaskUpdateRequest
from src.app.features.tasks.application.dtos.task_dto_mapper import map_entity_to_response
from src.app.features.tasks.application.exceptions.task_exception import TaskAccessDeniedException, TaskNotFoundException
from src.app.features.tasks.domain.repositories.task_repository import TaskRepository
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class UpdateTaskUseCase:
    """Partially update a task, validating project ownership."""

    def __init__(self, task_repository: TaskRepository, project_repository: ProjectRepository):
        self._task_repository = task_repository
        self._project_repository = project_repository

    async def execute(self, task_id: str, owner_id: str, payload: TaskUpdateRequest) -> TaskResponse:
        task = await self._task_repository.find_by_id(EntityId.from_string(task_id))

        if not task:
            raise TaskNotFoundException(task_id)

        project = await self._project_repository.find_by_id(task.project_id)

        if not project or str(project.owner_id) != owner_id:
            raise TaskAccessDeniedException(task_id, owner_id)

        if payload.title is not None:
            task.update_title(payload.title.strip())

        if payload.description is not None:
            task.update_description(payload.description.strip())

        if payload.status is not None:
            task.update_status(payload.status)

        if payload.priority is not None:
            task.update_priority(payload.priority)

        updated = await self._task_repository.update(task)
        log.info(f"Task updated: {task_id}")
        return map_entity_to_response(updated)
