"""Unit tests for note routes (HTTP behavior)."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.features.notes.application.dtos.note_dto import NoteResponse, NoteListResponse, NoteConvertResponse
from src.app.features.notes.application.exceptions.note_exception import (
    NoteNotFoundException, NoteAccessDeniedException, NoteAlreadyConvertedException,
)
from src.app.features.notes.domain.entities.note_type import NoteType
from src.app.features.notes.presentation.web.routes.note_routes import project_notes_router, notes_router


def _note_response(project_id: str) -> NoteResponse:
    return NoteResponse(
        id=str(uuid4()), project_id=project_id, content="Test note",
        note_type=NoteType.RAW, is_enriched=False, ai_suggestion=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = str(uuid4())
    return user


@pytest.fixture
def app(mock_user):
    from src.app.features.auth.presentation.web.dependencies import get_current_user
    from src.app.features.notes.presentation.web.dependencies import (
        get_create_note_use_case, get_get_all_notes_use_case,
        get_get_note_by_id_use_case, get_update_note_use_case,
        get_delete_note_use_case, get_convert_note_use_case,
    )
    test_app = FastAPI()
    test_app.include_router(project_notes_router, prefix="/api/v1/projects")
    test_app.include_router(notes_router, prefix="/api/v1/notes")
    test_app.dependency_overrides[get_current_user] = lambda: mock_user
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestCreateNoteRoute:
    def test_returns_201(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_create_note_use_case
        project_id = str(uuid4())
        uc = AsyncMock()
        uc.execute.return_value = _note_response(project_id)
        app.dependency_overrides[get_create_note_use_case] = lambda: uc

        r = client.post(f"/api/v1/projects/{project_id}/notes", json={"content": "Hello"})
        assert r.status_code == 201

    def test_returns_422_for_empty_content(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_create_note_use_case
        uc = AsyncMock()
        app.dependency_overrides[get_create_note_use_case] = lambda: uc
        r = client.post(f"/api/v1/projects/{uuid4()}/notes", json={"content": ""})
        assert r.status_code == 422

    def test_returns_403_on_access_denied(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_create_note_use_case
        uc = AsyncMock()
        uc.execute.side_effect = NoteAccessDeniedException(str(uuid4()), mock_user.id)
        app.dependency_overrides[get_create_note_use_case] = lambda: uc
        r = client.post(f"/api/v1/projects/{uuid4()}/notes", json={"content": "Hi"})
        assert r.status_code == 403


class TestGetAllNotesRoute:
    def test_returns_200_with_list(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_get_all_notes_use_case
        project_id = str(uuid4())
        uc = AsyncMock()
        uc.execute.return_value = NoteListResponse(items=[_note_response(project_id)], total=1, page=1, size=50)
        app.dependency_overrides[get_get_all_notes_use_case] = lambda: uc
        r = client.get(f"/api/v1/projects/{project_id}/notes")
        assert r.status_code == 200
        assert r.json()["total"] == 1


class TestGetNoteByIdRoute:
    def test_returns_200(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_get_note_by_id_use_case
        note_id = str(uuid4())
        uc = AsyncMock()
        uc.execute.return_value = _note_response(str(uuid4()))
        app.dependency_overrides[get_get_note_by_id_use_case] = lambda: uc
        r = client.get(f"/api/v1/notes/{note_id}")
        assert r.status_code == 200

    def test_returns_404(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_get_note_by_id_use_case
        uc = AsyncMock()
        uc.execute.side_effect = NoteNotFoundException(str(uuid4()))
        app.dependency_overrides[get_get_note_by_id_use_case] = lambda: uc
        r = client.get(f"/api/v1/notes/{uuid4()}")
        assert r.status_code == 404


class TestDeleteNoteRoute:
    def test_returns_204(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_delete_note_use_case
        uc = AsyncMock()
        uc.execute.return_value = None
        app.dependency_overrides[get_delete_note_use_case] = lambda: uc
        r = client.delete(f"/api/v1/notes/{uuid4()}")
        assert r.status_code == 204

    def test_returns_404(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_delete_note_use_case
        uc = AsyncMock()
        uc.execute.side_effect = NoteNotFoundException(str(uuid4()))
        app.dependency_overrides[get_delete_note_use_case] = lambda: uc
        r = client.delete(f"/api/v1/notes/{uuid4()}")
        assert r.status_code == 404


class TestConvertNoteRoute:
    def test_returns_200_on_convert(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_convert_note_use_case
        uc = AsyncMock()
        uc.execute.return_value = NoteConvertResponse(
            message="Converted to task successfully.", created_task_id=str(uuid4())
        )
        app.dependency_overrides[get_convert_note_use_case] = lambda: uc
        r = client.post(f"/api/v1/notes/{uuid4()}/convert", json={"targetType": "task"})
        assert r.status_code == 200
        assert r.json()["createdTaskId"] is not None

    def test_returns_400_when_already_converted(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_convert_note_use_case
        uc = AsyncMock()
        uc.execute.side_effect = NoteAlreadyConvertedException(str(uuid4()))
        app.dependency_overrides[get_convert_note_use_case] = lambda: uc
        r = client.post(f"/api/v1/notes/{uuid4()}/convert", json={"targetType": "task"})
        assert r.status_code == 400

    def test_returns_422_for_raw_target_type(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_convert_note_use_case
        uc = AsyncMock()
        app.dependency_overrides[get_convert_note_use_case] = lambda: uc
        r = client.post(f"/api/v1/notes/{uuid4()}/convert", json={"targetType": "raw"})
        assert r.status_code == 422


class TestUpdateNoteRoute:
    def test_returns_200_on_content_update(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_update_note_use_case
        uc = AsyncMock()
        uc.execute.return_value = _note_response(str(uuid4()))
        app.dependency_overrides[get_update_note_use_case] = lambda: uc
        r = client.patch(f"/api/v1/notes/{uuid4()}", json={"content": "Updated"})
        assert r.status_code == 200

    def test_returns_404_when_note_missing(self, app, client, mock_user):
        from src.app.features.notes.presentation.web.dependencies import get_update_note_use_case
        uc = AsyncMock()
        uc.execute.side_effect = NoteNotFoundException(str(uuid4()))
        app.dependency_overrides[get_update_note_use_case] = lambda: uc
        r = client.patch(f"/api/v1/notes/{uuid4()}", json={"content": "Updated"})
        assert r.status_code == 404
