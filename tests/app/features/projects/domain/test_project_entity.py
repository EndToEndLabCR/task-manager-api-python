"""Unit tests for ProjectEntity and ProjectStatus."""
import pytest
from datetime import datetime
from uuid import uuid4

from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.value_objects.entity_id import EntityId


class TestProjectStatus:
    """Tests for the ProjectStatus enum."""

    def test_active_value(self):
        assert ProjectStatus.ACTIVE == "active"
        assert ProjectStatus.ACTIVE.value == "active"

    def test_archived_value(self):
        assert ProjectStatus.ARCHIVED == "archived"
        assert ProjectStatus.ARCHIVED.value == "archived"

    def test_completed_value(self):
        assert ProjectStatus.COMPLETED == "completed"
        assert ProjectStatus.COMPLETED.value == "completed"

    def test_is_string_enum(self):
        """ProjectStatus should be usable as a string."""
        assert isinstance(ProjectStatus.ACTIVE, str)
        assert str(ProjectStatus.ACTIVE.value) == "active"
        assert ProjectStatus.ACTIVE == "active"

    def test_from_value(self):
        """Should be able to construct from string value."""
        assert ProjectStatus("active") == ProjectStatus.ACTIVE
        assert ProjectStatus("archived") == ProjectStatus.ARCHIVED
        assert ProjectStatus("completed") == ProjectStatus.COMPLETED

    def test_invalid_value_raises(self):
        """Should raise ValueError for invalid status."""
        with pytest.raises(ValueError):
            ProjectStatus("invalid")


class TestProjectEntity:
    """Tests for the ProjectEntity domain entity."""

    def _create_entity(self, **overrides) -> ProjectEntity:
        """Helper to create a ProjectEntity with defaults."""
        defaults = {
            "name": "Test Project",
            "description": "A test project description",
            "owner_id": EntityId.generate(),
            "status": ProjectStatus.ACTIVE,
        }
        defaults.update(overrides)
        return ProjectEntity(**defaults)

    def test_create_with_defaults(self):
        """Should create entity with auto-generated ID and timestamps."""
        owner_id = EntityId.generate()
        entity = ProjectEntity(
            name="My Project",
            description="Description",
            owner_id=owner_id,
        )

        assert entity.name == "My Project"
        assert entity.description == "Description"
        assert entity.owner_id == owner_id
        assert entity.status == ProjectStatus.ACTIVE
        assert entity.id is not None
        assert entity.created_at is not None
        assert entity.updated_at is not None

    def test_create_with_explicit_id(self):
        """Should accept an explicit EntityId."""
        explicit_id = EntityId.from_string(str(uuid4()))
        entity = self._create_entity(id=explicit_id)

        assert entity.id == explicit_id

    def test_create_with_explicit_status(self):
        """Should accept an explicit status."""
        entity = self._create_entity(status=ProjectStatus.COMPLETED)

        assert entity.status == ProjectStatus.COMPLETED

    def test_update_name(self):
        """Should update name and mark entity as updated."""
        entity = self._create_entity()
        original_updated_at = entity.updated_at

        entity.update_name("New Name")

        assert entity.name == "New Name"
        assert entity.updated_at >= original_updated_at

    def test_update_description(self):
        """Should update description and mark entity as updated."""
        entity = self._create_entity()
        original_updated_at = entity.updated_at

        entity.update_description("New Description")

        assert entity.description == "New Description"
        assert entity.updated_at >= original_updated_at

    def test_update_status(self):
        """Should update status and mark entity as updated."""
        entity = self._create_entity(status=ProjectStatus.ACTIVE)

        entity.update_status(ProjectStatus.COMPLETED)

        assert entity.status == ProjectStatus.COMPLETED

    def test_archive(self):
        """Should set status to ARCHIVED."""
        entity = self._create_entity(status=ProjectStatus.ACTIVE)

        entity.archive()

        assert entity.status == ProjectStatus.ARCHIVED

    def test_create_with_timestamps(self):
        """Should accept explicit timestamps."""
        now = datetime(2026, 1, 1, 12, 0, 0)
        entity = self._create_entity(created_at=now, updated_at=now)

        assert entity.created_at == now
        assert entity.updated_at == now

    def test_inherits_base_entity(self):
        """Should have BaseEntity properties (id, created_at, updated_at)."""
        entity = self._create_entity()

        assert hasattr(entity, "id")
        assert hasattr(entity, "created_at")
        assert hasattr(entity, "updated_at")
        assert hasattr(entity, "mark_as_updated")
