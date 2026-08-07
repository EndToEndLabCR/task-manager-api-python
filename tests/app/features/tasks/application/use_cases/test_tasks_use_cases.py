"""Unit tests for Tasks use cases."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.app.features.tasks.application.dtos.task_dto import TaskCreateRequest, TaskUpdateRequest
from src.app.features.tasks.application.exceptions.task_exception import TaskNotFoundException, TaskAccessDeniedException
from src.app.features.tasks.application.use_cases.create_task import CreateTaskUseCase
from src.app.features.tasks.application.use_cases.get_all_tasks import GetAllTasksUseCase
from src.app.features.tasks.application.use_cases.update_task import UpdateTaskUseCase
from src.app.features.tasks.application.use_cases.delete_task import DeleteTaskUseCase
from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.app.features.notes.domain.entities.note_entity import NoteEntity
from src.shared.domain.value_objects.entity_id import EntityId


def _make_project(owner_id: str) -> ProjectEntity:
    return ProjectEntity(
        id=EntityId.generate(), name="P", description="D",
        owner_id=EntityId.from_string(owner_id), status=ProjectStatus.ACTIVE,
    )


def _make_task(project_id: str) -> TaskEntity:
    return TaskEntity(
        id=EntityId.generate(),
        project_id=EntityId.from_string(project_id),
        title="Fix bug",
    )


def _make_note(project_id: str) -> NoteEntity:
    return NoteEntity(
        id=EntityId.generate(),
        project_id=EntityId.from_string(project_id),
        content="Note content",
    )


@pytest.fixture
def task_repo():
    return AsyncMock()


@pytest.fixture
def project_repo():
    return AsyncMock()


@pytest.fixture
def note_repo():
    return AsyncMock()


class TestCreateTaskUseCase:
    @pytest.mark.asyncio
    async def test_creates_task_successfully(self, task_repo, project_repo, note_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        task_repo.save.return_value = _make_task(project_id)

        uc = CreateTaskUseCase(task_repo, project_repo, note_repo)
        result = await uc.execute(project_id, owner_id, TaskCreateRequest(title="Fix bug"))

        assert result.title == "Fix bug"
        task_repo.save.assert_called_once()
        note_repo.find_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_when_not_owner(self, task_repo, project_repo, note_repo):
        project_repo.find_by_id.return_value = _make_project(str(uuid4()))
        uc = CreateTaskUseCase(task_repo, project_repo, note_repo)

        with pytest.raises(TaskAccessDeniedException):
            await uc.execute(str(uuid4()), str(uuid4()), TaskCreateRequest(title="x"))

    @pytest.mark.asyncio
    async def test_raises_when_project_not_found(self, task_repo, project_repo, note_repo):
        project_repo.find_by_id.return_value = None
        uc = CreateTaskUseCase(task_repo, project_repo, note_repo)

        with pytest.raises(TaskAccessDeniedException):
            await uc.execute(str(uuid4()), str(uuid4()), TaskCreateRequest(title="x"))

    @pytest.mark.asyncio
    async def test_creates_task_with_valid_source_note(self, task_repo, project_repo, note_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.find_by_id.return_value = _make_note(project_id)
        task_repo.save.return_value = _make_task(project_id)

        uc = CreateTaskUseCase(task_repo, project_repo, note_repo)
        result = await uc.execute(
            project_id, owner_id,
            TaskCreateRequest(title="From note", source_note_id=str(uuid4())),
        )

        assert result.title == "Fix bug"
        task_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_when_source_note_not_found(self, task_repo, project_repo, note_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.find_by_id.return_value = None

        uc = CreateTaskUseCase(task_repo, project_repo, note_repo)
        with pytest.raises(ValueError):
            await uc.execute(
                project_id, owner_id,
                TaskCreateRequest(title="x", source_note_id=str(uuid4())),
            )
        task_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_when_source_note_belongs_to_other_project(self, task_repo, project_repo, note_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.find_by_id.return_value = _make_note(str(uuid4()))  # different project

        uc = CreateTaskUseCase(task_repo, project_repo, note_repo)
        with pytest.raises(ValueError):
            await uc.execute(
                project_id, owner_id,
                TaskCreateRequest(title="x", source_note_id=str(uuid4())),
            )
        task_repo.save.assert_not_called()


class TestGetAllTasksUseCase:
    @pytest.mark.asyncio
    async def test_returns_paginated_tasks(self, task_repo, project_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        task_repo.find_all_by_project_id.return_value = [_make_task(project_id) for _ in range(2)]
        task_repo.count_by_project_id.return_value = 2

        uc = GetAllTasksUseCase(task_repo, project_repo)
        result = await uc.execute(project_id, owner_id)

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_filters_passed_to_repo(self, task_repo, project_repo):
        owner_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        task_repo.find_all_by_project_id.return_value = []
        task_repo.count_by_project_id.return_value = 0

        uc = GetAllTasksUseCase(task_repo, project_repo)
        await uc.execute(str(uuid4()), owner_id, status=TaskStatus.TODO, priority=TaskPriority.HIGH, page=2, size=10)

        call_kwargs = task_repo.find_all_by_project_id.call_args
        assert call_kwargs[0][1] == TaskStatus.TODO
        assert call_kwargs[0][2] == TaskPriority.HIGH


class TestUpdateTaskUseCase:
    @pytest.mark.asyncio
    async def test_partial_update_status(self, task_repo, project_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        task = _make_task(project_id)
        task_repo.find_by_id.return_value = task
        project_repo.find_by_id.return_value = _make_project(owner_id)
        task_repo.update.return_value = task

        uc = UpdateTaskUseCase(task_repo, project_repo)
        await uc.execute(str(uuid4()), owner_id, TaskUpdateRequest(status=TaskStatus.DONE))

        assert task.status == TaskStatus.DONE

    @pytest.mark.asyncio
    async def test_raises_not_found(self, task_repo, project_repo):
        task_repo.find_by_id.return_value = None
        uc = UpdateTaskUseCase(task_repo, project_repo)

        with pytest.raises(TaskNotFoundException):
            await uc.execute(str(uuid4()), str(uuid4()), TaskUpdateRequest(title="x"))

    @pytest.mark.asyncio
    async def test_raises_access_denied(self, task_repo, project_repo):
        project_id = str(uuid4())
        task_repo.find_by_id.return_value = _make_task(project_id)
        project_repo.find_by_id.return_value = _make_project(str(uuid4()))

        uc = UpdateTaskUseCase(task_repo, project_repo)
        with pytest.raises(TaskAccessDeniedException):
            await uc.execute(str(uuid4()), str(uuid4()), TaskUpdateRequest(title="hack"))


class TestDeleteTaskUseCase:
    @pytest.mark.asyncio
    async def test_deletes_task(self, task_repo, project_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        task_repo.find_by_id.return_value = _make_task(project_id)
        project_repo.find_by_id.return_value = _make_project(owner_id)
        task_repo.delete.return_value = True

        uc = DeleteTaskUseCase(task_repo, project_repo)
        await uc.execute(str(uuid4()), owner_id)

        task_repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_not_found(self, task_repo, project_repo):
        task_repo.find_by_id.return_value = None
        uc = DeleteTaskUseCase(task_repo, project_repo)

        with pytest.raises(TaskNotFoundException):
            await uc.execute(str(uuid4()), str(uuid4()))
