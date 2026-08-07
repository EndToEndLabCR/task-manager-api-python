"""Unit tests for Notes use cases."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.app.features.notes.application.dtos.note_dto import NoteCreateRequest, NoteUpdateRequest, NoteConvertRequest
from src.app.features.notes.application.exceptions.note_exception import (
    NoteAccessDeniedException, NoteNotFoundException, NoteAlreadyConvertedException,
)
from src.app.features.notes.application.use_cases.create_note import CreateNoteUseCase
from src.app.features.notes.application.use_cases.get_all_notes import GetAllNotesUseCase
from src.app.features.notes.application.use_cases.get_note_by_id import GetNoteByIdUseCase
from src.app.features.notes.application.use_cases.update_note import UpdateNoteUseCase
from src.app.features.notes.application.use_cases.delete_note import DeleteNoteUseCase
from src.app.features.notes.application.use_cases.convert_note import ConvertNoteUseCase
from src.app.features.notes.domain.entities.note_entity import NoteEntity
from src.app.features.notes.domain.entities.note_type import NoteType
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.shared.domain.value_objects.entity_id import EntityId


def _make_project(owner_id: str) -> ProjectEntity:
    return ProjectEntity(
        id=EntityId.generate(),
        name="Test Project",
        description="Desc",
        owner_id=EntityId.from_string(owner_id),
        status=ProjectStatus.ACTIVE,
    )


def _make_note(project_id: str, note_type: NoteType = NoteType.RAW) -> NoteEntity:
    return NoteEntity(
        id=EntityId.generate(),
        project_id=EntityId.from_string(project_id),
        content="Some note content",
        note_type=note_type,
    )


@pytest.fixture
def note_repo():
    return AsyncMock()


@pytest.fixture
def project_repo():
    return AsyncMock()


class TestCreateNoteUseCase:
    @pytest.mark.asyncio
    async def test_creates_note_successfully(self, note_repo, project_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.save.return_value = _make_note(project_id)

        use_case = CreateNoteUseCase(note_repo, project_repo)
        result = await use_case.execute(project_id, owner_id, NoteCreateRequest(content="Hello"))

        assert result.content == "Some note content"
        note_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_access_denied_when_project_not_found(self, note_repo, project_repo):
        project_repo.find_by_id.return_value = None
        use_case = CreateNoteUseCase(note_repo, project_repo)

        with pytest.raises(NoteAccessDeniedException):
            await use_case.execute(str(uuid4()), str(uuid4()), NoteCreateRequest(content="Hi"))

    @pytest.mark.asyncio
    async def test_raises_access_denied_when_not_owner(self, note_repo, project_repo):
        project_repo.find_by_id.return_value = _make_project(str(uuid4()))
        use_case = CreateNoteUseCase(note_repo, project_repo)

        with pytest.raises(NoteAccessDeniedException):
            await use_case.execute(str(uuid4()), str(uuid4()), NoteCreateRequest(content="Hi"))


class TestGetAllNotesUseCase:
    @pytest.mark.asyncio
    async def test_returns_paginated_notes(self, note_repo, project_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        notes = [_make_note(project_id) for _ in range(3)]
        note_repo.find_all_by_project_id.return_value = notes
        note_repo.count_by_project_id.return_value = 3

        use_case = GetAllNotesUseCase(note_repo, project_repo)
        result = await use_case.execute(project_id, owner_id, None, 1, 50)

        assert result.total == 3
        assert len(result.items) == 3
        assert result.page == 1
        assert result.size == 50

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, note_repo, project_repo):
        owner_id = str(uuid4())
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.find_all_by_project_id.return_value = []
        note_repo.count_by_project_id.return_value = 0

        use_case = GetAllNotesUseCase(note_repo, project_repo)
        result = await use_case.execute(str(uuid4()), owner_id)

        assert result.total == 0
        assert result.items == []


class TestGetNoteByIdUseCase:
    @pytest.mark.asyncio
    async def test_returns_note(self, note_repo, project_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        note = _make_note(project_id)
        note_repo.find_by_id.return_value = note
        project_repo.find_by_id.return_value = _make_project(owner_id)

        use_case = GetNoteByIdUseCase(note_repo, project_repo)
        result = await use_case.execute(str(uuid4()), owner_id)

        assert result.content == "Some note content"

    @pytest.mark.asyncio
    async def test_raises_not_found(self, note_repo, project_repo):
        note_repo.find_by_id.return_value = None
        use_case = GetNoteByIdUseCase(note_repo, project_repo)

        with pytest.raises(NoteNotFoundException):
            await use_case.execute(str(uuid4()), str(uuid4()))


class TestUpdateNoteUseCase:
    @pytest.mark.asyncio
    async def test_updates_content(self, note_repo, project_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        note = _make_note(project_id)
        note_repo.find_by_id.return_value = note
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.update.return_value = note

        use_case = UpdateNoteUseCase(note_repo, project_repo)
        await use_case.execute(str(uuid4()), owner_id, NoteUpdateRequest(content="New content"))

        assert note.content == "New content"

    @pytest.mark.asyncio
    async def test_raises_not_found(self, note_repo, project_repo):
        note_repo.find_by_id.return_value = None
        use_case = UpdateNoteUseCase(note_repo, project_repo)

        with pytest.raises(NoteNotFoundException):
            await use_case.execute(str(uuid4()), str(uuid4()), NoteUpdateRequest(content="x"))


class TestDeleteNoteUseCase:
    @pytest.mark.asyncio
    async def test_deletes_note(self, note_repo, project_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        note_repo.find_by_id.return_value = _make_note(project_id)
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.delete.return_value = True

        use_case = DeleteNoteUseCase(note_repo, project_repo)
        await use_case.execute(str(uuid4()), owner_id)

        note_repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_not_found(self, note_repo, project_repo):
        note_repo.find_by_id.return_value = None
        use_case = DeleteNoteUseCase(note_repo, project_repo)

        with pytest.raises(NoteNotFoundException):
            await use_case.execute(str(uuid4()), str(uuid4()))


class TestConvertNoteUseCase:
    @pytest.fixture
    def task_repo(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_converts_raw_to_task_and_creates_task(self, note_repo, project_repo, task_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        note = _make_note(project_id, NoteType.RAW)
        note_repo.find_by_id.return_value = note
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.update.return_value = note
        created_task = TaskEntity(
            id=EntityId.generate(),
            project_id=note.project_id,
            title="Some note content",
            description=note.content,
            source_note_id=note.id,
        )
        task_repo.save.return_value = created_task

        use_case = ConvertNoteUseCase(note_repo, project_repo, task_repo)
        result = await use_case.execute(str(uuid4()), owner_id, NoteConvertRequest(target_type=NoteType.TASK))

        assert "task" in result.message
        assert note.note_type == NoteType.TASK
        assert note.is_enriched is True
        assert result.created_task_id == str(created_task.id)
        task_repo.save.assert_called_once()
        saved_task = task_repo.save.call_args.args[0]
        assert saved_task.title == "Some note content"
        assert saved_task.source_note_id == note.id
        assert saved_task.project_id == note.project_id

    @pytest.mark.asyncio
    async def test_converts_raw_to_architecture_decision_without_task(self, note_repo, project_repo, task_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        note = _make_note(project_id, NoteType.RAW)
        note_repo.find_by_id.return_value = note
        project_repo.find_by_id.return_value = _make_project(owner_id)
        note_repo.update.return_value = note

        use_case = ConvertNoteUseCase(note_repo, project_repo, task_repo)
        result = await use_case.execute(
            str(uuid4()), owner_id, NoteConvertRequest(target_type=NoteType.ARCHITECTURE_DECISION)
        )

        assert note.note_type == NoteType.ARCHITECTURE_DECISION
        assert result.created_task_id is None
        task_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_already_converted(self, note_repo, project_repo, task_repo):
        owner_id = str(uuid4())
        project_id = str(uuid4())
        note = _make_note(project_id, NoteType.TASK)  # already converted
        note_repo.find_by_id.return_value = note
        project_repo.find_by_id.return_value = _make_project(owner_id)

        use_case = ConvertNoteUseCase(note_repo, project_repo, task_repo)
        with pytest.raises(NoteAlreadyConvertedException):
            await use_case.execute(str(uuid4()), owner_id, NoteConvertRequest(target_type=NoteType.ARCHITECTURE_DECISION))
        task_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_rejects_raw_as_target_type(self):
        with pytest.raises(ValueError):
            NoteConvertRequest(target_type=NoteType.RAW)
