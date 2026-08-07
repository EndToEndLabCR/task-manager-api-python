"""Unit tests for note model mapper and repository impl."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import sqlalchemy.exc

from src.app.features.notes.domain.entities.note_type import NoteType
from src.app.features.notes.infrastructure.repository.note_model_mapper import map_model_to_entity
from src.app.features.notes.infrastructure.repository.note_repository_impl import (
    NoteRepositoryImpl, DatabaseConnectionError,
)
from src.app.features.notes.domain.entities.note_entity import NoteEntity
from src.shared.domain.value_objects.entity_id import EntityId


def _mock_model(**kw):
    m = MagicMock()
    m.id = kw.get("id", uuid4())
    m.project_id = kw.get("project_id", uuid4())
    m.content = kw.get("content", "Note content")
    m.note_type = kw.get("note_type", "raw")
    m.is_enriched = kw.get("is_enriched", False)
    m.ai_suggestion = kw.get("ai_suggestion", None)
    m.created_at = kw.get("created_at", datetime(2026, 1, 1, tzinfo=timezone.utc))
    m.updated_at = kw.get("updated_at", datetime(2026, 1, 1, tzinfo=timezone.utc))
    return m


class TestNoteModelMapper:
    def test_maps_all_fields(self):
        model = _mock_model()
        entity = map_model_to_entity(model)
        assert isinstance(entity, NoteEntity)
        assert entity.id.value == model.id
        assert entity.project_id.value == model.project_id
        assert entity.content == model.content
        assert entity.note_type == NoteType.RAW
        assert entity.is_enriched is False

    def test_maps_task_type(self):
        entity = map_model_to_entity(_mock_model(note_type="task"))
        assert entity.note_type == NoteType.TASK

    def test_maps_architecture_decision(self):
        entity = map_model_to_entity(_mock_model(note_type="architecture_decision"))
        assert entity.note_type == NoteType.ARCHITECTURE_DECISION

    def test_maps_ai_suggestion(self):
        suggestion = {"type": "TASK", "confidence": 0.9}
        entity = map_model_to_entity(_mock_model(ai_suggestion=suggestion))
        assert entity.ai_suggestion == suggestion


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repo(mock_session):
    return NoteRepositoryImpl(mock_session)


class TestNoteRepositoryImpl:
    @pytest.mark.asyncio
    async def test_find_by_id_returns_none_when_missing(self, repo, mock_session):
        mock_session.get.return_value = None
        result = await repo.find_by_id(EntityId(uuid4()))
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_id_returns_entity(self, repo, mock_session):
        mock_session.get.return_value = _mock_model()
        result = await repo.find_by_id(EntityId(uuid4()))
        assert result is not None
        assert result.content == "Note content"

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_not_found(self, repo, mock_session):
        mock_session.get.return_value = None
        result = await repo.delete(EntityId(uuid4()))
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_returns_true(self, repo, mock_session):
        mock_session.get.return_value = _mock_model()
        result = await repo.delete(EntityId(uuid4()))
        assert result is True
        mock_session.delete.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_id_raises_db_connection_error(self, repo, mock_session):
        mock_session.get.side_effect = sqlalchemy.exc.OperationalError("x", None, None)
        with pytest.raises(DatabaseConnectionError):
            await repo.find_by_id(EntityId(uuid4()))
