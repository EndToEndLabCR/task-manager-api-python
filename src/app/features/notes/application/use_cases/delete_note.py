from src.app.features.notes.application.exceptions.note_exception import (
    NoteAccessDeniedException,
    NoteNotFoundException,
)
from src.app.features.notes.domain.repositories.note_repository import NoteRepository
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class DeleteNoteUseCase:
    """Delete a note, validating project ownership."""

    def __init__(self, note_repository: NoteRepository, project_repository: ProjectRepository):
        self._note_repository = note_repository
        self._project_repository = project_repository

    async def execute(self, note_id: str, owner_id: str) -> None:
        note = await self._note_repository.find_by_id(EntityId.from_string(note_id))

        if not note:
            raise NoteNotFoundException(note_id)

        project = await self._project_repository.find_by_id(note.project_id)

        if not project or str(project.owner_id) != owner_id:
            raise NoteAccessDeniedException(note_id, owner_id)

        await self._note_repository.delete(EntityId.from_string(note_id))
        log.info(f"Note deleted: {note_id}")
