from src.app.features.notes.application.dtos.note_dto import NoteCreateRequest, NoteResponse
from src.app.features.notes.application.dtos.note_dto_mapper import map_create_request_to_entity, map_entity_to_response
from src.app.features.notes.application.exceptions.note_exception import NoteAccessDeniedException
from src.app.features.notes.domain.repositories.note_repository import NoteRepository
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class CreateNoteUseCase:
    """Create a quick note inside a project workspace."""

    def __init__(self, note_repository: NoteRepository, project_repository: ProjectRepository):
        self._note_repository = note_repository
        self._project_repository = project_repository

    async def execute(self, project_id: str, owner_id: str, payload: NoteCreateRequest) -> NoteResponse:
        project = await self._project_repository.find_by_id(EntityId.from_string(project_id))

        if not project:
            raise NoteAccessDeniedException(project_id, owner_id)

        if str(project.owner_id) != owner_id:
            raise NoteAccessDeniedException(project_id, owner_id)

        entity = map_create_request_to_entity(payload, project_id)
        saved = await self._note_repository.save(entity)

        log.info(f"Note created: {saved.id} in project: {project_id}")
        return map_entity_to_response(saved)
