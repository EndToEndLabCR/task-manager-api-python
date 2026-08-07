"""Unit tests for DeleteProjectUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.app.features.projects.application.exceptions.project_exception import (
    ProjectAccessDeniedException,
    ProjectNotFoundException,
)
from src.app.features.projects.application.use_cases.delete_project import DeleteProjectUseCase
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.value_objects.entity_id import EntityId


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def use_case(mock_repository):
    return DeleteProjectUseCase(project_repository=mock_repository)


class TestDeleteProjectUseCase:
    """Tests for DeleteProjectUseCase."""

    @pytest.mark.asyncio
    async def test_deletes_project_successfully(self, use_case, mock_repository):
        """Should delete a project and return success message."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = ProjectEntity(
            id=EntityId.from_string(project_id),
            name="Test",
            description="Desc",
            owner_id=EntityId.from_string(owner_id),
            status=ProjectStatus.ACTIVE,
        )
        mock_repository.find_by_id.return_value = entity
        mock_repository.delete.return_value = True

        result = await use_case.execute(project_id, owner_id)

        assert "deleted successfully" in result.message
        assert project_id in result.message
        mock_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_not_found_when_project_missing(self, use_case, mock_repository):
        """Should raise ProjectNotFoundException when project does not exist."""
        mock_repository.find_by_id.return_value = None

        with pytest.raises(ProjectNotFoundException):
            await use_case.execute(str(uuid4()), str(uuid4()))

    @pytest.mark.asyncio
    async def test_raises_access_denied_when_not_owner(self, use_case, mock_repository):
        """Should raise ProjectAccessDeniedException when not the owner."""
        owner_id = str(uuid4())
        other_user = str(uuid4())
        project_id = str(uuid4())
        entity = ProjectEntity(
            id=EntityId.from_string(project_id),
            name="Test",
            description="Desc",
            owner_id=EntityId.from_string(owner_id),
            status=ProjectStatus.ACTIVE,
        )
        mock_repository.find_by_id.return_value = entity

        with pytest.raises(ProjectAccessDeniedException):
            await use_case.execute(project_id, other_user)

        mock_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_value_error_for_invalid_project_id(self, use_case, mock_repository):
        """Should raise ValueError for invalid UUID format."""
        with pytest.raises(ValueError):
            await use_case.execute("bad-uuid", str(uuid4()))
