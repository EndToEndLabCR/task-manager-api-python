"""Unit tests for GetProjectByIdUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.app.features.projects.application.exceptions.project_exception import (
    ProjectAccessDeniedException,
    ProjectNotFoundException,
)
from src.app.features.projects.application.use_cases.get_project_by_id import GetProjectByIdUseCase
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.value_objects.entity_id import EntityId


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def use_case(mock_repository):
    return GetProjectByIdUseCase(project_repository=mock_repository)


class TestGetProjectByIdUseCase:
    """Tests for GetProjectByIdUseCase."""

    @pytest.mark.asyncio
    async def test_returns_project_when_owner_matches(self, use_case, mock_repository):
        """Should return project response when owner_id matches."""
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

        result = await use_case.execute(project_id, owner_id)

        assert result.id == project_id
        assert result.name == "Test"
        assert result.owner_id == owner_id

    @pytest.mark.asyncio
    async def test_raises_not_found_when_project_missing(self, use_case, mock_repository):
        """Should raise ProjectNotFoundException when project does not exist."""
        mock_repository.find_by_id.return_value = None
        project_id = str(uuid4())

        with pytest.raises(ProjectNotFoundException) as exc_info:
            await use_case.execute(project_id, str(uuid4()))

        assert project_id in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_raises_access_denied_when_not_owner(self, use_case, mock_repository):
        """Should raise ProjectAccessDeniedException when user is not the owner."""
        owner_id = str(uuid4())
        other_user_id = str(uuid4())
        project_id = str(uuid4())

        entity = ProjectEntity(
            id=EntityId.from_string(project_id),
            name="Test",
            description="Desc",
            owner_id=EntityId.from_string(owner_id),
            status=ProjectStatus.ACTIVE,
        )
        mock_repository.find_by_id.return_value = entity

        with pytest.raises(ProjectAccessDeniedException) as exc_info:
            await use_case.execute(project_id, other_user_id)

        assert project_id in str(exc_info.value)
        assert other_user_id in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_raises_value_error_for_invalid_uuid(self, use_case, mock_repository):
        """Should raise ValueError for invalid project_id format."""
        with pytest.raises(ValueError):
            await use_case.execute("not-a-uuid", str(uuid4()))
