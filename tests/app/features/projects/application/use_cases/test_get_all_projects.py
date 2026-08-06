"""Unit tests for GetAllProjectsUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.app.features.projects.application.use_cases.get_all_projects import GetAllProjectsUseCase
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.value_objects.entity_id import EntityId


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def use_case(mock_repository):
    return GetAllProjectsUseCase(project_repository=mock_repository)


class TestGetAllProjectsUseCase:
    """Tests for GetAllProjectsUseCase."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_projects(self, use_case, mock_repository):
        """Should return empty list with total 0."""
        owner_id = str(uuid4())
        mock_repository.find_all_by_owner_id.return_value = []

        result = await use_case.execute(owner_id)

        assert result.projects == []
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_returns_all_projects_for_owner(self, use_case, mock_repository):
        """Should return all projects belonging to the owner."""
        owner_id = str(uuid4())
        owner_entity_id = EntityId.from_string(owner_id)

        projects = [
            ProjectEntity(
                id=EntityId.generate(),
                name=f"Project {i}",
                description=f"Desc {i}",
                owner_id=owner_entity_id,
                status=ProjectStatus.ACTIVE,
            )
            for i in range(3)
        ]
        mock_repository.find_all_by_owner_id.return_value = projects

        result = await use_case.execute(owner_id)

        assert len(result.projects) == 3
        assert result.total == 3
        assert result.projects[0].name == "Project 0"
        assert result.projects[1].name == "Project 1"
        assert result.projects[2].name == "Project 2"

    @pytest.mark.asyncio
    async def test_passes_correct_owner_id_to_repository(self, use_case, mock_repository):
        """Should call repository with the correct EntityId."""
        owner_id = str(uuid4())
        mock_repository.find_all_by_owner_id.return_value = []

        await use_case.execute(owner_id)

        call_arg = mock_repository.find_all_by_owner_id.call_args[0][0]
        assert str(call_arg) == owner_id

    @pytest.mark.asyncio
    async def test_raises_value_error_for_invalid_owner_id(self, use_case, mock_repository):
        """Should raise ValueError for invalid owner_id format."""
        with pytest.raises(ValueError):
            await use_case.execute("invalid-uuid")
