"""Unit tests for NoteEntity and NoteType."""
import pytest
from src.app.features.notes.domain.entities.note_entity import NoteEntity
from src.app.features.notes.domain.entities.note_type import NoteType
from src.shared.domain.value_objects.entity_id import EntityId


class TestNoteType:
    def test_values(self):
        assert NoteType.RAW == "raw"
        assert NoteType.TASK == "task"
        assert NoteType.ARCHITECTURE_DECISION == "architecture_decision"

    def test_from_string(self):
        assert NoteType("raw") == NoteType.RAW
        assert NoteType("task") == NoteType.TASK

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            NoteType("invalid")


class TestNoteEntity:
    def _make(self, **kw) -> NoteEntity:
        defaults = dict(project_id=EntityId.generate(), content="Test note")
        defaults.update(kw)
        return NoteEntity(**defaults)

    def test_defaults(self):
        note = self._make()
        assert note.note_type == NoteType.RAW
        assert note.is_enriched is False
        assert note.ai_suggestion is None
        assert note.id is not None

    def test_update_content(self):
        note = self._make()
        note.update_content("Updated")
        assert note.content == "Updated"

    def test_convert_type_marks_enriched(self):
        note = self._make()
        note.convert_type(NoteType.TASK)
        assert note.note_type == NoteType.TASK
        assert note.is_enriched is True

    def test_convert_to_architecture_decision(self):
        note = self._make()
        note.convert_type(NoteType.ARCHITECTURE_DECISION)
        assert note.note_type == NoteType.ARCHITECTURE_DECISION

    def test_mark_as_enriched_stores_suggestion(self):
        note = self._make()
        suggestion = {"suggested_type": "TASK", "confidence": 0.9}
        note.mark_as_enriched(suggestion)
        assert note.is_enriched is True
        assert note.ai_suggestion == suggestion

    def test_explicit_id_used(self):
        eid = EntityId.generate()
        note = self._make(id=eid)
        assert note.id == eid
