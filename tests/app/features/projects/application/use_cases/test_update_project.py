"""Unit tests for UpdateProjectUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.app.features.projects.application.dtos.project_dto import ProjectUpdateRequest
from src.app.features.projects.application.exceptions.project_exception import (
    ProjectAccessDeniedException,
    ProjectNameAlreadyExistsException,
    ProjectNotFoundException,
)
from src.app.features.projects.application.use_cases.update_project import UpdateProjectUseCase
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.value_objects.entity_id import EntityId


@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.exists_by_owner_id_and_name.return_value = False
    return repo


@pytest.fixture
def use_case(mock_repository):
    return UpdateProjectUseCase(project_repository=mock_repository)


def _create_project(project_id: str, owner_id: str) -> ProjectEntity:
    return ProjectEntity(
        id=EntityId.from_string(project_id),
        name="Original Name",
        description="Original Desc",
        owner_id=EntityId.from_string(owner_id),
        status=ProjectStatus.ACTIVE,
    )


class TestUpdateProjectUseCase:
    """Tests for UpdateProjectUseCase."""

    @pytest.mark.asyncio
    async def test_updates_name_only(self, use_case, mock_repository):
        """Should update only name when only name is provided."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.update.return_value = entity

        payload = ProjectUpdateRequest(name="Updated Name")
        result = await use_case.execute(project_id, payload, owner_id)

        assert result.name == "Updated Name"
        assert result.description == "Original Desc"

    @pytest.mark.asyncio
    async def test_updates_description_only(self, use_case, mock_repository):
        """Should update only description when only description is provided."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.update.return_value = entity

        payload = ProjectUpdateRequest(description="Updated Desc")
        await use_case.execute(project_id, payload, owner_id)

        # Entity should have been mutated
        assert entity.description == "Updated Desc"
        assert entity.name == "Original Name"

    @pytest.mark.asyncio
    async def test_updates_status_only(self, use_case, mock_repository):
        """Should update only status when only status is provided."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.update.return_value = entity

        payload = ProjectUpdateRequest(status=ProjectStatus.COMPLETED)
        await use_case.execute(project_id, payload, owner_id)

        assert entity.status == ProjectStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_updates_all_fields(self, use_case, mock_repository):
        """Should update all fields when all are provided."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.update.return_value = entity

        payload = ProjectUpdateRequest(
            name="New Name",
            description="New Desc",
            status=ProjectStatus.ARCHIVED,
        )
        await use_case.execute(project_id, payload, owner_id)

        assert entity.name == "New Name"
        assert entity.description == "New Desc"
        assert entity.status == ProjectStatus.ARCHIVED

    @pytest.mark.asyncio
    async def test_raises_not_found(self, use_case, mock_repository):
        """Should raise ProjectNotFoundException when project does not exist."""
        mock_repository.find_by_id.return_value = None
        project_id = str(uuid4())

        payload = ProjectUpdateRequest(name="Name")

        with pytest.raises(ProjectNotFoundException):
            await use_case.execute(project_id, payload, str(uuid4()))

    @pytest.mark.asyncio
    async def test_raises_access_denied(self, use_case, mock_repository):
        """Should raise ProjectAccessDeniedException when not the owner."""
        owner_id = str(uuid4())
        other_user = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity

        payload = ProjectUpdateRequest(name="Hacked")

        with pytest.raises(ProjectAccessDeniedException):
            await use_case.execute(project_id, payload, other_user)

    @pytest.mark.asyncio
    async def test_no_update_when_no_fields_provided(self, use_case, mock_repository):
        """Should not mutate entity when no fields are set in payload."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.update.return_value = entity

        payload = ProjectUpdateRequest()  # No fields
        await use_case.execute(project_id, payload, owner_id)

        assert entity.name == "Original Name"
        assert entity.description == "Original Desc"
        assert entity.status == ProjectStatus.ACTIVE
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_when_new_name_already_exists(self, use_case, mock_repository):
        """Should raise ProjectNameAlreadyExistsException on duplicate name."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.exists_by_owner_id_and_name.return_value = True

        payload = ProjectUpdateRequest(name="Taken Name")

        with pytest.raises(ProjectNameAlreadyExistsException):
            await use_case.execute(project_id, payload, owner_id)

        mock_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_same_name_does_not_trigger_uniqueness_check(self, use_case, mock_repository):
        """Keeping the same name should not check uniqueness nor fail."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.update.return_value = entity

        payload = ProjectUpdateRequest(name="Original Name")
        await use_case.execute(project_id, payload, owner_id)

        mock_repository.exists_by_owner_id_and_name.assert_not_called()

    @pytest.mark.asyncio
    async def test_updates_github_repo_url(self, use_case, mock_repository):
        """Should update github_repo_url when provided."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.update.return_value = entity

        repo_url = "https://github.com/user/repo"
        payload = ProjectUpdateRequest(github_repo_url=repo_url)
        await use_case.execute(project_id, payload, owner_id)

        assert entity.github_repo_url == repo_url

    @pytest.mark.asyncio
    async def test_raises_not_found_when_update_returns_none(self, use_case, mock_repository):
        """Should raise ProjectNotFoundException if the row vanished mid-update."""
        owner_id = str(uuid4())
        project_id = str(uuid4())
        entity = _create_project(project_id, owner_id)

        mock_repository.find_by_id.return_value = entity
        mock_repository.update.return_value = None

        payload = ProjectUpdateRequest(description="New Desc")

        with pytest.raises(ProjectNotFoundException):
            await use_case.execute(project_id, payload, owner_id)
