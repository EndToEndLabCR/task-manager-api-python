from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.app.features.auth.presentation.web.dependencies import get_current_user
from src.app.features.projects.application.dtos.project_dto import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)
from src.app.features.projects.application.exceptions.project_exception import (
    ProjectAccessDeniedException,
    ProjectNameAlreadyExistsException,
    ProjectNotFoundException,
)
from src.app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from src.app.features.projects.application.use_cases.delete_project import DeleteProjectUseCase
from src.app.features.projects.application.use_cases.get_all_projects import GetAllProjectsUseCase
from src.app.features.projects.application.use_cases.get_project_by_id import GetProjectByIdUseCase
from src.app.features.projects.application.use_cases.update_project import UpdateProjectUseCase
from src.app.features.projects.presentation.web.dependencies import (
    get_create_project_use_case,
    get_delete_project_use_case,
    get_get_all_projects_use_case,
    get_get_project_by_id_use_case,
    get_update_project_use_case,
)

router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def get_all_projects(
    current_user=Depends(get_current_user),
    use_case: GetAllProjectsUseCase = Depends(get_get_all_projects_use_case),
) -> ProjectListResponse:
    """Retrieve all projects for the authenticated user."""
    try:
        return await use_case.execute(current_user.id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: UUID,
    current_user=Depends(get_current_user),
    use_case: GetProjectByIdUseCase = Depends(get_get_project_by_id_use_case),
) -> ProjectResponse:
    """Retrieve a specific project by ID, validating ownership."""
    try:
        return await use_case.execute(str(project_id), current_user.id)

    except ProjectNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ProjectAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    current_user=Depends(get_current_user),
    use_case: CreateProjectUseCase = Depends(get_create_project_use_case),
) -> ProjectResponse:
    """Create a new project for the authenticated user."""
    try:
        return await use_case.execute(payload, current_user.id)

    except ProjectNameAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateProjectUseCase = Depends(get_update_project_use_case),
) -> ProjectResponse:
    """Update an existing project, validating ownership."""
    try:
        return await use_case.execute(str(project_id), payload, current_user.id)

    except ProjectNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ProjectAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ProjectNameAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user=Depends(get_current_user),
    use_case: DeleteProjectUseCase = Depends(get_delete_project_use_case),
) -> None:
    """Delete a project, validating ownership."""
    try:
        await use_case.execute(str(project_id), current_user.id)

    except ProjectNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ProjectAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
