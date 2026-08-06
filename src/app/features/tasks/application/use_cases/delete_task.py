from src.app.features.tasks.application.exceptions.task_exception import TaskAccessDeniedException, TaskNotFoundException
from src.app.features.tasks.domain.repositories.task_repository import TaskRepository
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class DeleteTaskUseCase:
    """Delete a task, validating project ownership."""

    def __init__(self, task_repository: TaskRepository, project_repository: ProjectRepository):
        self._task_repository = task_repository
        self._project_repository = project_repository

    async def execute(self, task_id: str, owner_id: str) -> None:
        task = await self._task_repository.find_by_id(EntityId.from_string(task_id))

        if not task:
            raise TaskNotFoundException(task_id)

        project = await self._project_repository.find_by_id(task.project_id)

        if not project or str(project.owner_id) != owner_id:
            raise TaskAccessDeniedException(task_id, owner_id)

        await self._task_repository.delete(EntityId.from_string(task_id))
        log.info(f"Task deleted: {task_id}")
