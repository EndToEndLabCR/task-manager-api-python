from src.app.features.notes.application.dtos.note_dto import NoteConvertRequest, NoteConvertResponse
from src.app.features.notes.application.exceptions.note_exception import (
    NoteAccessDeniedException,
    NoteAlreadyConvertedException,
    NoteNotFoundException,
)
from src.app.features.notes.domain.entities.note_type import NoteType
from src.app.features.notes.domain.repositories.note_repository import NoteRepository
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.app.features.tasks.domain.repositories.task_repository import TaskRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log

# Max length of the tasks.title column; note content is truncated to fit.
TASK_TITLE_MAX_LENGTH = 200


def _derive_task_title(content: str) -> str:
    """Derive a task title from the note content (first line, truncated)."""
    first_line = content.strip().splitlines()[0].strip()
    if len(first_line) <= TASK_TITLE_MAX_LENGTH:
        return first_line
    return first_line[: TASK_TITLE_MAX_LENGTH - 3] + "..."


class ConvertNoteUseCase:
    """Convert a RAW note into a TASK or ARCHITECTURE_DECISION.

    When the target is TASK, a new Task is created from the note content
    (source_note_id points back to the note) and its id is returned.
    In both cases the note keeps existing, changes type and is marked
    as enriched.
    """

    def __init__(
        self,
        note_repository: NoteRepository,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
    ):
        self._note_repository = note_repository
        self._project_repository = project_repository
        self._task_repository = task_repository

    async def execute(self, note_id: str, owner_id: str, payload: NoteConvertRequest) -> NoteConvertResponse:
        note = await self._note_repository.find_by_id(EntityId.from_string(note_id))

        if not note:
            raise NoteNotFoundException(note_id)

        project = await self._project_repository.find_by_id(note.project_id)

        if not project or str(project.owner_id) != owner_id:
            raise NoteAccessDeniedException(note_id, owner_id)

        if note.note_type != NoteType.RAW:
            raise NoteAlreadyConvertedException(note_id)

        created_task_id = None
        if payload.target_type == NoteType.TASK:
            task = TaskEntity(
                project_id=note.project_id,
                title=_derive_task_title(note.content),
                description=note.content,
                source_note_id=note.id,
            )
            saved_task = await self._task_repository.save(task)
            created_task_id = str(saved_task.id)
            log.info(f"Task {created_task_id} created from note {note_id}")

        note.convert_type(payload.target_type)
        await self._note_repository.update(note)

        log.info(f"Note {note_id} converted to {payload.target_type.value}")
        return NoteConvertResponse(
            message=f"Note converted to {payload.target_type.value} successfully.",
            created_task_id=created_task_id,
        )
