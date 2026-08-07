"""Unit tests for CreateProjectUseCase."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.app.features.projects.application.dtos.project_dto import ProjectCreateRequest
from src.app.features.projects.application.exceptions.project_exception import (
    ProjectNameAlreadyExistsException,
)
from src.app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.value_objects.entity_id import EntityId


@pytest.fixture
def mock_repository():
    """Create a mock project repository."""
    repo = AsyncMock()
    repo.exists_by_owner_id_and_name.return_value = False
    return repo


@pytest.fixture
def use_case(mock_repository):
    """Create a CreateProjectUseCase with mocked dependencies."""
    return CreateProjectUseCase(project_repository=mock_repository)


class TestCreateProjectUseCase:
    """Tests for CreateProjectUseCase."""

    @pytest.mark.asyncio
    async def test_creates_project_successfully(self, use_case, mock_repository):
        """Should create a project and return a response DTO."""
        owner_id = str(uuid4())
        payload = ProjectCreateRequest(
            name="My Project",
            description="Test description",
            status=ProjectStatus.ACTIVE,
        )

        saved_entity = ProjectEntity(
            id=EntityId.generate(),
            name="My Project",
            description="Test description",
            owner_id=EntityId.from_string(owner_id),
            status=ProjectStatus.ACTIVE,
        )
        mock_repository.save.return_value = saved_entity

        result = await use_case.execute(payload, owner_id)

        assert result.name == "My Project"
        assert result.description == "Test description"
        assert result.status == ProjectStatus.ACTIVE
        assert result.owner_id == owner_id
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_project_with_default_status(self, use_case, mock_repository):
        """Should default to ACTIVE status when not specified."""
        owner_id = str(uuid4())
        payload = ProjectCreateRequest(name="Project")

        saved_entity = ProjectEntity(
            id=EntityId.generate(),
            name="Project",
            description="",
            owner_id=EntityId.from_string(owner_id),
            status=ProjectStatus.ACTIVE,
        )
        mock_repository.save.return_value = saved_entity

        result = await use_case.execute(payload, owner_id)

        assert result.status == ProjectStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_repository_called_with_correct_entity(self, use_case, mock_repository):
        """Should pass a well-formed entity to the repository."""
        owner_id = str(uuid4())
        payload = ProjectCreateRequest(
            name="Test",
            description="Desc",
            status=ProjectStatus.COMPLETED,
        )

        mock_repository.save.return_value = ProjectEntity(
            id=EntityId.generate(),
            name="Test",
            description="Desc",
            owner_id=EntityId.from_string(owner_id),
            status=ProjectStatus.COMPLETED,
        )

        await use_case.execute(payload, owner_id)

        saved_arg = mock_repository.save.call_args[0][0]
        assert isinstance(saved_arg, ProjectEntity)
        assert saved_arg.name == "Test"
        assert saved_arg.description == "Desc"
        assert str(saved_arg.owner_id) == owner_id
        assert saved_arg.status == ProjectStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_propagates_repository_exception(self, use_case, mock_repository):
        """Should propagate exceptions raised by the repository."""
        owner_id = str(uuid4())
        payload = ProjectCreateRequest(name="Test")
        mock_repository.save.side_effect = Exception("DB error")

        with pytest.raises(Exception, match="DB error"):
            await use_case.execute(payload, owner_id)

    @pytest.mark.asyncio
    async def test_raises_when_name_already_exists(self, use_case, mock_repository):
        """Should raise ProjectNameAlreadyExistsException on duplicate name."""
        owner_id = str(uuid4())
        payload = ProjectCreateRequest(name="Duplicated")
        mock_repository.exists_by_owner_id_and_name.return_value = True

        with pytest.raises(ProjectNameAlreadyExistsException):
            await use_case.execute(payload, owner_id)

        mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_project_with_github_repo_url(self, use_case, mock_repository):
        """Should pass github_repo_url through to the saved entity."""
        owner_id = str(uuid4())
        repo_url = "https://github.com/user/repo"
        payload = ProjectCreateRequest(name="With Repo", github_repo_url=repo_url)

        mock_repository.save.return_value = ProjectEntity(
            id=EntityId.generate(),
            name="With Repo",
            description="",
            owner_id=EntityId.from_string(owner_id),
            status=ProjectStatus.ACTIVE,
            github_repo_url=repo_url,
        )

        result = await use_case.execute(payload, owner_id)

        assert result.github_repo_url == repo_url
        saved_arg = mock_repository.save.call_args[0][0]
        assert saved_arg.github_repo_url == repo_url
