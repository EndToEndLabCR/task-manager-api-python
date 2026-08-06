from typing import Optional

from src.app.features.notes.application.dtos.note_dto import NoteListResponse
from src.app.features.notes.application.dtos.note_dto_mapper import map_entity_to_response
from src.app.features.notes.application.exceptions.note_exception import NoteAccessDeniedException
from src.app.features.notes.domain.entities.note_type import NoteType
from src.app.features.notes.domain.repositories.note_repository import NoteRepository
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class GetAllNotesUseCase:
    """Retrieve paginated notes for a project, optionally filtered by type."""

    def __init__(self, note_repository: NoteRepository, project_repository: ProjectRepository):
        self._note_repository = note_repository
        self._project_repository = project_repository

    async def execute(
        self,
        project_id: str,
        owner_id: str,
        note_type: Optional[NoteType] = None,
        page: int = 1,
        size: int = 50,
    ) -> NoteListResponse:
        project = await self._project_repository.find_by_id(EntityId.from_string(project_id))

        if not project:
            raise NoteAccessDeniedException(project_id, owner_id)

        if str(project.owner_id) != owner_id:
            raise NoteAccessDeniedException(project_id, owner_id)

        project_entity_id = EntityId.from_string(project_id)
        notes = await self._note_repository.find_all_by_project_id(project_entity_id, note_type, page, size)
        total = await self._note_repository.count_by_project_id(project_entity_id, note_type)

        log.info(f"Retrieved {len(notes)} notes for project: {project_id}")
        return NoteListResponse(
            items=[map_entity_to_response(n) for n in notes],
            total=total,
            page=page,
            size=size,
        )
