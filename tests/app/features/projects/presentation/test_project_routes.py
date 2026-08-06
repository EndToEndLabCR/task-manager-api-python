"""Unit tests for project routes (presentation layer).

These tests mock use cases and validate HTTP behavior:
status codes, response shapes, error handling.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.features.projects.application.dtos.project_dto import (
    ProjectListResponse,
    ProjectResponse,
    DeleteResponse,
)
from src.app.features.projects.application.exceptions.project_exception import (
    ProjectAccessDeniedException,
    ProjectNotFoundException,
)
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.app.features.projects.presentation.web.routes.project_routes import router


# --- Fixtures ---

@pytest.fixture
def mock_current_user():
    """Mock authenticated user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.username = "testuser"
    user.email = "test@test.com"
    return user


@pytest.fixture
def app(mock_current_user):
    """Create a test FastAPI app with mocked dependencies."""
    from src.app.features.auth.presentation.web.dependencies import get_current_user

    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/v1/projects")

    # Override auth dependency
    test_app.dependency_overrides[get_current_user] = lambda: mock_current_user

    return test_app


@pytest.fixture
def client(app):
    """Create a TestClient for the test app."""
    return TestClient(app)


def _project_response(owner_id: str, project_id: str = None) -> ProjectResponse:
    """Create a sample ProjectResponse."""
    return ProjectResponse(
        id=project_id or str(uuid4()),
        name="Test Project",
        description="A description",
        owner_id=owner_id,
        status=ProjectStatus.ACTIVE,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


class TestGetAllProjects:
    """Tests for GET /api/v1/projects."""

    def test_returns_200_with_projects(self, app, client, mock_current_user):
        """Should return 200 with list of projects."""
        from src.app.features.projects.presentation.web.dependencies import get_get_all_projects_use_case

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = ProjectListResponse(
            projects=[_project_response(mock_current_user.id)],
            total=1,
        )
        app.dependency_overrides[get_get_all_projects_use_case] = lambda: mock_use_case

        response = client.get("/api/v1/projects/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["projects"]) == 1

    def test_returns_200_with_empty_list(self, app, client, mock_current_user):
        """Should return 200 with empty list when no projects exist."""
        from src.app.features.projects.presentation.web.dependencies import get_get_all_projects_use_case

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = ProjectListResponse(projects=[], total=0)
        app.dependency_overrides[get_get_all_projects_use_case] = lambda: mock_use_case

        response = client.get("/api/v1/projects/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["projects"] == []


class TestGetProjectById:
    """Tests for GET /api/v1/projects/{project_id}."""

    def test_returns_200_when_found(self, app, client, mock_current_user):
        """Should return 200 with project data."""
        from src.app.features.projects.presentation.web.dependencies import get_get_project_by_id_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = _project_response(
            mock_current_user.id, project_id
        )
        app.dependency_overrides[get_get_project_by_id_use_case] = lambda: mock_use_case

        response = client.get(f"/api/v1/projects/{project_id}")

        assert response.status_code == 200
        assert response.json()["id"] == project_id

    def test_returns_404_when_not_found(self, app, client, mock_current_user):
        """Should return 404 when project does not exist."""
        from src.app.features.projects.presentation.web.dependencies import get_get_project_by_id_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ProjectNotFoundException(project_id)
        app.dependency_overrides[get_get_project_by_id_use_case] = lambda: mock_use_case

        response = client.get(f"/api/v1/projects/{project_id}")

        assert response.status_code == 404

    def test_returns_403_when_not_owner(self, app, client, mock_current_user):
        """Should return 403 when user does not own the project."""
        from src.app.features.projects.presentation.web.dependencies import get_get_project_by_id_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ProjectAccessDeniedException(
            project_id, mock_current_user.id
        )
        app.dependency_overrides[get_get_project_by_id_use_case] = lambda: mock_use_case

        response = client.get(f"/api/v1/projects/{project_id}")

        assert response.status_code == 403


class TestCreateProject:
    """Tests for POST /api/v1/projects."""

    def test_returns_201_on_success(self, app, client, mock_current_user):
        """Should return 201 with created project."""
        from src.app.features.projects.presentation.web.dependencies import get_create_project_use_case

        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = _project_response(mock_current_user.id)
        app.dependency_overrides[get_create_project_use_case] = lambda: mock_use_case

        response = client.post(
            "/api/v1/projects/",
            json={"name": "New Project", "description": "Desc"},
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Test Project"

    def test_returns_422_for_invalid_payload(self, app, client, mock_current_user):
        """Should return 422 when name is missing."""
        from src.app.features.projects.presentation.web.dependencies import get_create_project_use_case

        mock_use_case = AsyncMock()
        app.dependency_overrides[get_create_project_use_case] = lambda: mock_use_case

        response = client.post("/api/v1/projects/", json={})

        assert response.status_code == 422

    def test_returns_422_for_name_too_long(self, app, client, mock_current_user):
        """Should return 422 when name exceeds 100 chars."""
        from src.app.features.projects.presentation.web.dependencies import get_create_project_use_case

        mock_use_case = AsyncMock()
        app.dependency_overrides[get_create_project_use_case] = lambda: mock_use_case

        response = client.post(
            "/api/v1/projects/",
            json={"name": "x" * 101},
        )

        assert response.status_code == 422


class TestUpdateProject:
    """Tests for PUT /api/v1/projects/{project_id}."""

    def test_returns_200_on_success(self, app, client, mock_current_user):
        """Should return 200 with updated project."""
        from src.app.features.projects.presentation.web.dependencies import get_update_project_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = _project_response(
            mock_current_user.id, project_id
        )
        app.dependency_overrides[get_update_project_use_case] = lambda: mock_use_case

        response = client.put(
            f"/api/v1/projects/{project_id}",
            json={"name": "Updated"},
        )

        assert response.status_code == 200

    def test_returns_404_when_not_found(self, app, client, mock_current_user):
        """Should return 404 when project does not exist."""
        from src.app.features.projects.presentation.web.dependencies import get_update_project_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ProjectNotFoundException(project_id)
        app.dependency_overrides[get_update_project_use_case] = lambda: mock_use_case

        response = client.put(
            f"/api/v1/projects/{project_id}",
            json={"name": "Updated"},
        )

        assert response.status_code == 404

    def test_returns_403_when_not_owner(self, app, client, mock_current_user):
        """Should return 403 when not the owner."""
        from src.app.features.projects.presentation.web.dependencies import get_update_project_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ProjectAccessDeniedException(
            project_id, mock_current_user.id
        )
        app.dependency_overrides[get_update_project_use_case] = lambda: mock_use_case

        response = client.put(
            f"/api/v1/projects/{project_id}",
            json={"name": "Hacked"},
        )

        assert response.status_code == 403


class TestDeleteProject:
    """Tests for DELETE /api/v1/projects/{project_id}."""

    def test_returns_204_on_success(self, app, client, mock_current_user):
        """Should return 204 No Content on successful delete."""
        from src.app.features.projects.presentation.web.dependencies import get_delete_project_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = DeleteResponse(
            message=f"Project {project_id} deleted"
        )
        app.dependency_overrides[get_delete_project_use_case] = lambda: mock_use_case

        response = client.delete(f"/api/v1/projects/{project_id}")

        assert response.status_code == 204

    def test_returns_404_when_not_found(self, app, client, mock_current_user):
        """Should return 404 when project does not exist."""
        from src.app.features.projects.presentation.web.dependencies import get_delete_project_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ProjectNotFoundException(project_id)
        app.dependency_overrides[get_delete_project_use_case] = lambda: mock_use_case

        response = client.delete(f"/api/v1/projects/{project_id}")

        assert response.status_code == 404

    def test_returns_403_when_not_owner(self, app, client, mock_current_user):
        """Should return 403 when not the owner."""
        from src.app.features.projects.presentation.web.dependencies import get_delete_project_use_case

        project_id = str(uuid4())
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ProjectAccessDeniedException(
            project_id, mock_current_user.id
        )
        app.dependency_overrides[get_delete_project_use_case] = lambda: mock_use_case

        response = client.delete(f"/api/v1/projects/{project_id}")

        assert response.status_code == 403
