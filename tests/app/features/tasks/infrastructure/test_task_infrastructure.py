"""Unit tests for task model mapper and repository impl."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import sqlalchemy.exc

from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.infrastructure.repository.task_model_mapper import map_model_to_entity
from src.app.features.tasks.infrastructure.repository.task_repository_impl import (
    TaskRepositoryImpl, DatabaseConnectionError,
)
from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.shared.domain.value_objects.entity_id import EntityId


def _mock_model(**kw):
    m = MagicMock()
    m.id = kw.get("id", uuid4())
    m.project_id = kw.get("project_id", uuid4())
    m.title = kw.get("title", "Fix bug")
    m.description = kw.get("description", None)
    m.status = kw.get("status", "todo")
    m.priority = kw.get("priority", "medium")
    m.source_note_id = kw.get("source_note_id", None)
    m.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    m.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return m


class TestTaskModelMapper:
    def test_maps_all_fields(self):
        model = _mock_model()
        entity = map_model_to_entity(model)
        assert isinstance(entity, TaskEntity)
        assert entity.title == "Fix bug"
        assert entity.status == TaskStatus.TODO
        assert entity.priority == TaskPriority.MEDIUM
        assert entity.source_note_id is None

    def test_maps_in_progress(self):
        entity = map_model_to_entity(_mock_model(status="in_progress"))
        assert entity.status == TaskStatus.IN_PROGRESS

    def test_maps_high_priority(self):
        entity = map_model_to_entity(_mock_model(priority="high"))
        assert entity.priority == TaskPriority.HIGH

    def test_maps_source_note_id(self):
        note_id = uuid4()
        entity = map_model_to_entity(_mock_model(source_note_id=note_id))
        assert entity.source_note_id is not None
        assert entity.source_note_id.value == note_id


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repo(mock_session):
    return TaskRepositoryImpl(mock_session)


class TestTaskRepositoryImpl:
    @pytest.mark.asyncio
    async def test_find_by_id_returns_none(self, repo, mock_session):
        mock_session.get.return_value = None
        result = await repo.find_by_id(EntityId(uuid4()))
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_id_returns_entity(self, repo, mock_session):
        mock_session.get.return_value = _mock_model()
        result = await repo.find_by_id(EntityId(uuid4()))
        assert result is not None
        assert result.title == "Fix bug"

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

    @pytest.mark.asyncio
    async def test_raises_db_connection_error(self, repo, mock_session):
        mock_session.get.side_effect = sqlalchemy.exc.OperationalError("x", None, None)
        with pytest.raises(DatabaseConnectionError):
            await repo.find_by_id(EntityId(uuid4()))
