from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.notes.application.use_cases.convert_note import ConvertNoteUseCase
from src.app.features.notes.application.use_cases.create_note import CreateNoteUseCase
from src.app.features.notes.application.use_cases.delete_note import DeleteNoteUseCase
from src.app.features.notes.application.use_cases.get_all_notes import GetAllNotesUseCase
from src.app.features.notes.application.use_cases.get_note_by_id import GetNoteByIdUseCase
from src.app.features.notes.application.use_cases.update_note import UpdateNoteUseCase
from src.app.features.notes.infrastructure.repository.note_repository_impl import NoteRepositoryImpl
from src.app.features.projects.infrastructure.repository.project_repository_impl import ProjectRepositoryImpl
from src.app.features.tasks.infrastructure.repository.task_repository_impl import TaskRepositoryImpl
from src.app.features.auth.presentation.web.dependencies import get_database_session


async def get_note_repository(session: AsyncSession = Depends(get_database_session)) -> NoteRepositoryImpl:
    return NoteRepositoryImpl(session)


async def get_project_repository_for_notes(session: AsyncSession = Depends(get_database_session)) -> ProjectRepositoryImpl:
    return ProjectRepositoryImpl(session)


async def get_task_repository_for_notes(session: AsyncSession = Depends(get_database_session)) -> TaskRepositoryImpl:
    return TaskRepositoryImpl(session)


async def get_create_note_use_case(
    note_repo: NoteRepositoryImpl = Depends(get_note_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_notes),
) -> CreateNoteUseCase:
    return CreateNoteUseCase(note_repo, project_repo)


async def get_get_all_notes_use_case(
    note_repo: NoteRepositoryImpl = Depends(get_note_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_notes),
) -> GetAllNotesUseCase:
    return GetAllNotesUseCase(note_repo, project_repo)


async def get_get_note_by_id_use_case(
    note_repo: NoteRepositoryImpl = Depends(get_note_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_notes),
) -> GetNoteByIdUseCase:
    return GetNoteByIdUseCase(note_repo, project_repo)


async def get_update_note_use_case(
    note_repo: NoteRepositoryImpl = Depends(get_note_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_notes),
) -> UpdateNoteUseCase:
    return UpdateNoteUseCase(note_repo, project_repo)


async def get_delete_note_use_case(
    note_repo: NoteRepositoryImpl = Depends(get_note_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_notes),
) -> DeleteNoteUseCase:
    return DeleteNoteUseCase(note_repo, project_repo)


async def get_convert_note_use_case(
    note_repo: NoteRepositoryImpl = Depends(get_note_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_notes),
    task_repo: TaskRepositoryImpl = Depends(get_task_repository_for_notes),
) -> ConvertNoteUseCase:
    return ConvertNoteUseCase(note_repo, project_repo, task_repo)
