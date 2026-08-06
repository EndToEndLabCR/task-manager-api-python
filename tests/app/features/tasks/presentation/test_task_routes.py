"""Unit tests for task routes (HTTP behavior)."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.features.tasks.application.dtos.task_dto import TaskResponse, TaskListResponse
from src.app.features.tasks.application.exceptions.task_exception import TaskNotFoundException, TaskAccessDeniedException
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.presentation.web.routes.task_routes import project_tasks_router, tasks_router


def _task_response(project_id: str) -> TaskResponse:
    return TaskResponse(
        id=str(uuid4()), project_id=project_id, title="Fix bug",
        description=None, status=TaskStatus.TODO, priority=TaskPriority.MEDIUM,
        source_note_id=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_user():
    u = MagicMock()
    u.id = str(uuid4())
    return u


@pytest.fixture
def app(mock_user):
    from src.app.features.auth.presentation.web.dependencies import get_current_user
    test_app = FastAPI()
    test_app.include_router(project_tasks_router, prefix="/api/v1/projects")
    test_app.include_router(tasks_router, prefix="/api/v1/tasks")
    test_app.dependency_overrides[get_current_user] = lambda: mock_user
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestCreateTaskRoute:
    def test_returns_201(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_create_task_use_case
        project_id = str(uuid4())
        uc = AsyncMock()
        uc.execute.return_value = _task_response(project_id)
        app.dependency_overrides[get_create_task_use_case] = lambda: uc
        r = client.post(f"/api/v1/projects/{project_id}/tasks", json={"title": "Fix bug"})
        assert r.status_code == 201

    def test_returns_422_no_title(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_create_task_use_case
        uc = AsyncMock()
        app.dependency_overrides[get_create_task_use_case] = lambda: uc
        r = client.post(f"/api/v1/projects/{uuid4()}/tasks", json={})
        assert r.status_code == 422

    def test_returns_403_on_access_denied(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_create_task_use_case
        uc = AsyncMock()
        uc.execute.side_effect = TaskAccessDeniedException(str(uuid4()), mock_user.id)
        app.dependency_overrides[get_create_task_use_case] = lambda: uc
        r = client.post(f"/api/v1/projects/{uuid4()}/tasks", json={"title": "x"})
        assert r.status_code == 403


class TestGetAllTasksRoute:
    def test_returns_200(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_get_all_tasks_use_case
        project_id = str(uuid4())
        uc = AsyncMock()
        uc.execute.return_value = TaskListResponse(items=[_task_response(project_id)], total=1, page=1, size=50)
        app.dependency_overrides[get_get_all_tasks_use_case] = lambda: uc
        r = client.get(f"/api/v1/projects/{project_id}/tasks")
        assert r.status_code == 200
        assert r.json()["total"] == 1

    def test_accepts_status_filter(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_get_all_tasks_use_case
        uc = AsyncMock()
        uc.execute.return_value = TaskListResponse(items=[], total=0, page=1, size=50)
        app.dependency_overrides[get_get_all_tasks_use_case] = lambda: uc
        r = client.get(f"/api/v1/projects/{uuid4()}/tasks?status=todo&priority=high")
        assert r.status_code == 200


class TestUpdateTaskRoute:
    def test_returns_200(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_update_task_use_case
        task_id = str(uuid4())
        uc = AsyncMock()
        uc.execute.return_value = _task_response(str(uuid4()))
        app.dependency_overrides[get_update_task_use_case] = lambda: uc
        r = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "done"})
        assert r.status_code == 200

    def test_returns_404(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_update_task_use_case
        uc = AsyncMock()
        uc.execute.side_effect = TaskNotFoundException(str(uuid4()))
        app.dependency_overrides[get_update_task_use_case] = lambda: uc
        r = client.patch(f"/api/v1/tasks/{uuid4()}", json={"status": "done"})
        assert r.status_code == 404


class TestDeleteTaskRoute:
    def test_returns_204(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_delete_task_use_case
        uc = AsyncMock()
        uc.execute.return_value = None
        app.dependency_overrides[get_delete_task_use_case] = lambda: uc
        r = client.delete(f"/api/v1/tasks/{uuid4()}")
        assert r.status_code == 204

    def test_returns_403(self, app, client, mock_user):
        from src.app.features.tasks.presentation.web.dependencies import get_delete_task_use_case
        uc = AsyncMock()
        uc.execute.side_effect = TaskAccessDeniedException(str(uuid4()), str(uuid4()))
        app.dependency_overrides[get_delete_task_use_case] = lambda: uc
        r = client.delete(f"/api/v1/tasks/{uuid4()}")
        assert r.status_code == 403
