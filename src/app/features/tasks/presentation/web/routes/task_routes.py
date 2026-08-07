from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.features.tasks.application.dtos.task_dto import (
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskUpdateRequest,
)
from src.app.features.tasks.application.exceptions.task_exception import (
    TaskAccessDeniedException,
    TaskNotFoundException,
)
from src.app.features.tasks.application.use_cases.create_task import CreateTaskUseCase
from src.app.features.tasks.application.use_cases.delete_task import DeleteTaskUseCase
from src.app.features.tasks.application.use_cases.get_all_tasks import GetAllTasksUseCase
from src.app.features.tasks.application.use_cases.update_task import UpdateTaskUseCase
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.app.features.tasks.presentation.web.dependencies import (
    get_create_task_use_case,
    get_delete_task_use_case,
    get_get_all_tasks_use_case,
    get_update_task_use_case,
)
from src.app.features.auth.presentation.web.dependencies import get_current_user

# Router for /api/v1/projects/{project_id}/tasks
project_tasks_router = APIRouter()

# Router for /api/v1/tasks/{task_id}
tasks_router = APIRouter()


@project_tasks_router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: UUID,
    payload: TaskCreateRequest,
    current_user=Depends(get_current_user),
    use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
) -> TaskResponse:
    """Create a task inside a project workspace."""
    try:
        return await use_case.execute(str(project_id), current_user.id, payload)
    except TaskAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@project_tasks_router.get("/{project_id}/tasks", response_model=TaskListResponse)
async def get_all_tasks(
    project_id: UUID,
    task_status: Optional[TaskStatus] = Query(default=None, alias="status"),
    priority: Optional[TaskPriority] = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    current_user=Depends(get_current_user),
    use_case: GetAllTasksUseCase = Depends(get_get_all_tasks_use_case),
) -> TaskListResponse:
    """List tasks for a project, with optional status/priority filters and pagination."""
    try:
        return await use_case.execute(str(project_id), current_user.id, task_status, priority, page, size)
    except TaskAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@tasks_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    payload: TaskUpdateRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateTaskUseCase = Depends(get_update_task_use_case),
) -> TaskResponse:
    """Partially update a task (title, description, status, priority)."""
    try:
        return await use_case.execute(str(task_id), current_user.id, payload)
    except TaskNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TaskAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@tasks_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user=Depends(get_current_user),
    use_case: DeleteTaskUseCase = Depends(get_delete_task_use_case),
) -> None:
    """Delete a task permanently."""
    try:
        await use_case.execute(str(task_id), current_user.id)
    except TaskNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TaskAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
