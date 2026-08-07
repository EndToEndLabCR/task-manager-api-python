"""Unit tests for TaskEntity, TaskStatus, TaskPriority."""
import pytest
from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.shared.domain.value_objects.entity_id import EntityId


class TestTaskStatus:
    def test_values(self):
        assert TaskStatus.TODO == "todo"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.DONE == "done"

    def test_from_string(self):
        assert TaskStatus("todo") == TaskStatus.TODO
        assert TaskStatus("in_progress") == TaskStatus.IN_PROGRESS

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            TaskStatus("invalid")


class TestTaskPriority:
    def test_values(self):
        assert TaskPriority.LOW == "low"
        assert TaskPriority.MEDIUM == "medium"
        assert TaskPriority.HIGH == "high"

    def test_from_string(self):
        assert TaskPriority("high") == TaskPriority.HIGH


class TestTaskEntity:
    def _make(self, **kw) -> TaskEntity:
        defaults = dict(project_id=EntityId.generate(), title="Fix the bug")
        defaults.update(kw)
        return TaskEntity(**defaults)

    def test_defaults(self):
        task = self._make()
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM
        assert task.description is None
        assert task.source_note_id is None

    def test_update_title(self):
        task = self._make()
        task.update_title("New Title")
        assert task.title == "New Title"

    def test_update_status(self):
        task = self._make()
        task.update_status(TaskStatus.DONE)
        assert task.status == TaskStatus.DONE

    def test_update_priority(self):
        task = self._make()
        task.update_priority(TaskPriority.HIGH)
        assert task.priority == TaskPriority.HIGH

    def test_update_description(self):
        task = self._make()
        task.update_description("Some details")
        assert task.description == "Some details"

    def test_source_note_id_tracked(self):
        note_id = EntityId.generate()
        task = self._make(source_note_id=note_id)
        assert task.source_note_id == note_id
