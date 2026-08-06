"""Unit tests for project model mapper."""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.app.features.projects.infrastructure.repository.project_model_mapper import map_model_to_entity


class TestProjectModelMapper:
    """Tests for map_model_to_entity function."""

    def _create_mock_model(self, **overrides):
        """Create a mock ProjectModel with default values."""
        model = MagicMock()
        model.id = overrides.get("id", uuid4())
        model.name = overrides.get("name", "Test Project")
        model.description = overrides.get("description", "A test description")
        model.owner_id = overrides.get("owner_id", uuid4())
        model.status = overrides.get("status", "active")
        model.created_at = overrides.get("created_at", datetime(2026, 1, 1, tzinfo=timezone.utc))
        model.updated_at = overrides.get("updated_at", datetime(2026, 1, 2, tzinfo=timezone.utc))
        return model

    def test_maps_all_fields_correctly(self):
        """Should map all model fields to entity fields."""
        model = self._create_mock_model()

        entity = map_model_to_entity(model)

        assert isinstance(entity, ProjectEntity)
        assert entity.id.value == model.id
        assert entity.name == model.name
        assert entity.description == model.description
        assert entity.owner_id.value == model.owner_id
        assert entity.created_at == model.created_at
        assert entity.updated_at == model.updated_at

    def test_maps_active_status(self):
        """Should correctly map 'active' status string to enum."""
        model = self._create_mock_model(status="active")
        entity = map_model_to_entity(model)
        assert entity.status == ProjectStatus.ACTIVE

    def test_maps_archived_status(self):
        """Should correctly map 'archived' status string to enum."""
        model = self._create_mock_model(status="archived")
        entity = map_model_to_entity(model)
        assert entity.status == ProjectStatus.ARCHIVED

    def test_maps_completed_status(self):
        """Should correctly map 'completed' status string to enum."""
        model = self._create_mock_model(status="completed")
        entity = map_model_to_entity(model)
        assert entity.status == ProjectStatus.COMPLETED

    def test_maps_none_description(self):
        """Should handle None description."""
        model = self._create_mock_model(description=None)
        entity = map_model_to_entity(model)
        assert entity.description is None

    def test_entity_has_correct_entity_id_type(self):
        """Should wrap UUIDs in EntityId value objects."""
        from src.shared.domain.value_objects.entity_id import EntityId

        model = self._create_mock_model()
        entity = map_model_to_entity(model)

        assert isinstance(entity.id, EntityId)
        assert isinstance(entity.owner_id, EntityId)
