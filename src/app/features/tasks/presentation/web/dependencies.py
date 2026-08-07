from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.tasks.application.use_cases.create_task import CreateTaskUseCase
from src.app.features.tasks.application.use_cases.delete_task import DeleteTaskUseCase
from src.app.features.tasks.application.use_cases.get_all_tasks import GetAllTasksUseCase
from src.app.features.tasks.application.use_cases.update_task import UpdateTaskUseCase
from src.app.features.tasks.infrastructure.repository.task_repository_impl import TaskRepositoryImpl
from src.app.features.notes.infrastructure.repository.note_repository_impl import NoteRepositoryImpl
from src.app.features.projects.infrastructure.repository.project_repository_impl import ProjectRepositoryImpl
from src.app.features.auth.presentation.web.dependencies import get_database_session


async def get_task_repository(session: AsyncSession = Depends(get_database_session)) -> TaskRepositoryImpl:
    return TaskRepositoryImpl(session)


async def get_project_repository_for_tasks(session: AsyncSession = Depends(get_database_session)) -> ProjectRepositoryImpl:
    return ProjectRepositoryImpl(session)


async def get_note_repository_for_tasks(session: AsyncSession = Depends(get_database_session)) -> NoteRepositoryImpl:
    return NoteRepositoryImpl(session)


async def get_create_task_use_case(
    task_repo: TaskRepositoryImpl = Depends(get_task_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_tasks),
    note_repo: NoteRepositoryImpl = Depends(get_note_repository_for_tasks),
) -> CreateTaskUseCase:
    return CreateTaskUseCase(task_repo, project_repo, note_repo)


async def get_get_all_tasks_use_case(
    task_repo: TaskRepositoryImpl = Depends(get_task_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_tasks),
) -> GetAllTasksUseCase:
    return GetAllTasksUseCase(task_repo, project_repo)


async def get_update_task_use_case(
    task_repo: TaskRepositoryImpl = Depends(get_task_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_tasks),
) -> UpdateTaskUseCase:
    return UpdateTaskUseCase(task_repo, project_repo)


async def get_delete_task_use_case(
    task_repo: TaskRepositoryImpl = Depends(get_task_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository_for_tasks),
) -> DeleteTaskUseCase:
    return DeleteTaskUseCase(task_repo, project_repo)
