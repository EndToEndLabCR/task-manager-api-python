"""Unit tests for ProjectRepositoryImpl."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

import sqlalchemy.exc

from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.app.features.projects.infrastructure.repository.project_repository_impl import (
    ProjectRepositoryImpl,
    DatabaseConnectionError,
)
from src.shared.domain.value_objects.entity_id import EntityId


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    session = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """Create repository with mock session."""
    return ProjectRepositoryImpl(db_session=mock_session)


def _create_entity(owner_id=None, project_id=None) -> ProjectEntity:
    """Helper to create a test ProjectEntity."""
    return ProjectEntity(
        id=EntityId.from_string(project_id or str(uuid4())),
        name="Test Project",
        description="Test Description",
        owner_id=EntityId.from_string(owner_id or str(uuid4())),
        status=ProjectStatus.ACTIVE,
    )


class TestProjectRepositorySave:
    """Tests for save method."""

    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self, repository, mock_session):
        """Should add model to session and commit."""
        entity = _create_entity()
        mock_session.refresh = AsyncMock()

        with patch(
            "src.app.features.projects.infrastructure.repository.project_repository_impl.map_model_to_entity"
        ) as mock_mapper:
            mock_mapper.return_value = entity
            await repository.save(entity)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_rolls_back_on_integrity_error(self, repository, mock_session):
        """Should rollback on IntegrityError."""
        entity = _create_entity()
        mock_session.commit.side_effect = sqlalchemy.exc.IntegrityError(
            "duplicate", params=None, orig=None
        )

        with pytest.raises(sqlalchemy.exc.IntegrityError):
            await repository.save(entity)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_raises_db_connection_error(self, repository, mock_session):
        """Should raise DatabaseConnectionError on OperationalError."""
        entity = _create_entity()
        mock_session.commit.side_effect = sqlalchemy.exc.OperationalError(
            "conn failed", params=None, orig=None
        )

        with pytest.raises(DatabaseConnectionError):
            await repository.save(entity)

        mock_session.rollback.assert_called_once()


class TestProjectRepositoryFindById:
    """Tests for find_by_id method."""

    @pytest.mark.asyncio
    async def test_returns_entity_when_found(self, repository, mock_session):
        """Should return mapped entity when model exists."""
        project_id = uuid4()
        mock_model = MagicMock()
        mock_model.id = project_id
        mock_model.name = "Found"
        mock_model.description = "Desc"
        mock_model.owner_id = uuid4()
        mock_model.status = "active"
        mock_model.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        mock_model.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        mock_session.get.return_value = mock_model

        result = await repository.find_by_id(EntityId(project_id))

        assert result is not None
        assert result.name == "Found"
        mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, repository, mock_session):
        """Should return None when model is not found."""
        mock_session.get.return_value = None

        result = await repository.find_by_id(EntityId(uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_raises_db_connection_error(self, repository, mock_session):
        """Should raise DatabaseConnectionError on OperationalError."""
        mock_session.get.side_effect = sqlalchemy.exc.OperationalError(
            "timeout", params=None, orig=None
        )

        with pytest.raises(DatabaseConnectionError):
            await repository.find_by_id(EntityId(uuid4()))


class TestProjectRepositoryFindAllByOwnerId:
    """Tests for find_all_by_owner_id method."""

    @pytest.mark.asyncio
    async def test_returns_list_of_entities(self, repository, mock_session):
        """Should return list of mapped entities."""
        owner_id = uuid4()
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.name = "Project"
        mock_model.description = "Desc"
        mock_model.owner_id = owner_id
        mock_model.status = "active"
        mock_model.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        mock_model.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repository.find_all_by_owner_id(EntityId(owner_id))

        assert len(result) == 1
        assert result[0].name == "Project"

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_projects(self, repository, mock_session):
        """Should return empty list when owner has no projects."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await repository.find_all_by_owner_id(EntityId(uuid4()))

        assert result == []


class TestProjectRepositoryDelete:
    """Tests for delete method."""

    @pytest.mark.asyncio
    async def test_deletes_and_returns_true(self, repository, mock_session):
        """Should delete the model and return True."""
        project_id = uuid4()
        mock_model = MagicMock()
        mock_session.get.return_value = mock_model

        result = await repository.delete(EntityId(project_id))

        assert result is True
        mock_session.delete.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self, repository, mock_session):
        """Should return False when project does not exist."""
        mock_session.get.return_value = None

        result = await repository.delete(EntityId(uuid4()))

        assert result is False
        mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_rolls_back_on_error(self, repository, mock_session):
        """Should rollback on unexpected errors."""
        mock_model = MagicMock()
        mock_session.get.return_value = mock_model
        mock_session.commit.side_effect = Exception("unexpected")

        with pytest.raises(Exception):
            await repository.delete(EntityId(uuid4()))

        mock_session.rollback.assert_called_once()
