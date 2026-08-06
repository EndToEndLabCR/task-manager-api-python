from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.auth.presentation.web.dependencies import get_database_session
from src.app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from src.app.features.projects.application.use_cases.delete_project import DeleteProjectUseCase
from src.app.features.projects.application.use_cases.get_all_projects import GetAllProjectsUseCase
from src.app.features.projects.application.use_cases.get_project_by_id import GetProjectByIdUseCase
from src.app.features.projects.application.use_cases.update_project import UpdateProjectUseCase
from src.app.features.projects.infrastructure.repository.project_repository_impl import ProjectRepositoryImpl


# --- Infrastructure ---

async def get_project_repository(
    session: AsyncSession = Depends(get_database_session),
) -> ProjectRepositoryImpl:
    return ProjectRepositoryImpl(session)


# --- Use Cases ---

async def get_create_project_use_case(
    project_repository: ProjectRepositoryImpl = Depends(get_project_repository),
) -> CreateProjectUseCase:
    return CreateProjectUseCase(project_repository)


async def get_get_project_by_id_use_case(
    project_repository: ProjectRepositoryImpl = Depends(get_project_repository),
) -> GetProjectByIdUseCase:
    return GetProjectByIdUseCase(project_repository)


async def get_get_all_projects_use_case(
    project_repository: ProjectRepositoryImpl = Depends(get_project_repository),
) -> GetAllProjectsUseCase:
    return GetAllProjectsUseCase(project_repository)


async def get_update_project_use_case(
    project_repository: ProjectRepositoryImpl = Depends(get_project_repository),
) -> UpdateProjectUseCase:
    return UpdateProjectUseCase(project_repository)


async def get_delete_project_use_case(
    project_repository: ProjectRepositoryImpl = Depends(get_project_repository),
) -> DeleteProjectUseCase:
    return DeleteProjectUseCase(project_repository)
