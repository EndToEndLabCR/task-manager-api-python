from src.app.features.notes.domain.repositories.note_repository import NoteRepository
from src.app.features.tasks.application.dtos.task_dto import TaskCreateRequest, TaskResponse
from src.app.features.tasks.application.dtos.task_dto_mapper import map_create_request_to_entity, map_entity_to_response
from src.app.features.tasks.application.exceptions.task_exception import TaskAccessDeniedException
from src.app.features.tasks.domain.repositories.task_repository import TaskRepository
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class CreateTaskUseCase:
    """Create a lightweight task inside a project workspace."""

    def __init__(
        self,
        task_repository: TaskRepository,
        project_repository: ProjectRepository,
        note_repository: NoteRepository,
    ):
        self._task_repository = task_repository
        self._project_repository = project_repository
        self._note_repository = note_repository

    async def execute(self, project_id: str, owner_id: str, payload: TaskCreateRequest) -> TaskResponse:
        project = await self._project_repository.find_by_id(EntityId.from_string(project_id))

        if not project:
            raise TaskAccessDeniedException(project_id, owner_id)

        if str(project.owner_id) != owner_id:
            raise TaskAccessDeniedException(project_id, owner_id)

        if payload.source_note_id is not None:
            note = await self._note_repository.find_by_id(
                EntityId.from_string(payload.source_note_id)
            )
            if note is None or str(note.project_id) != project_id:
                raise ValueError(
                    f"Source note {payload.source_note_id} does not exist in project {project_id}."
                )

        entity = map_create_request_to_entity(payload, project_id)
        saved = await self._task_repository.save(entity)

        log.info(f"Task created: {saved.id} in project: {project_id}")
        return map_entity_to_response(saved)
