"""Unit tests for project DTO mapper functions."""
import pytest
from uuid import uuid4

from src.app.features.projects.application.dtos.project_dto import (
    ProjectCreateRequest,
    ProjectResponse,
)
from src.app.features.projects.application.dtos.project_dto_mapper import (
    map_create_request_to_entity,
    map_entity_to_response,
)
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.value_objects.entity_id import EntityId


class TestMapEntityToResponse:
    """Tests for map_entity_to_response function."""

    def test_maps_all_fields_correctly(self):
        """Should convert all entity fields to response DTO."""
        owner_id = EntityId.generate()
        entity = ProjectEntity(
            name="Test Project",
            description="Description here",
            owner_id=owner_id,
            status=ProjectStatus.ACTIVE,
        )

        response = map_entity_to_response(entity)

        assert isinstance(response, ProjectResponse)
        assert response.id == str(entity.id)
        assert response.name == "Test Project"
        assert response.description == "Description here"
        assert response.owner_id == str(owner_id)
        assert response.status == ProjectStatus.ACTIVE
        assert response.created_at == entity.created_at
        assert response.updated_at == entity.updated_at

    def test_maps_none_description(self):
        """Should handle None description."""
        entity = ProjectEntity(
            name="Project",
            description=None,
            owner_id=EntityId.generate(),
        )

        response = map_entity_to_response(entity)

        assert response.description is None

    def test_maps_different_statuses(self):
        """Should correctly map all status values."""
        for status in ProjectStatus:
            entity = ProjectEntity(
                name="Project",
                description="Desc",
                owner_id=EntityId.generate(),
                status=status,
            )
            response = map_entity_to_response(entity)
            assert response.status == status


class TestMapCreateRequestToEntity:
    """Tests for map_create_request_to_entity function."""

    def test_maps_create_request_to_entity(self):
        """Should create a valid ProjectEntity from request DTO."""
        owner_id = str(uuid4())
        payload = ProjectCreateRequest(
            name="New Project",
            description="Some description",
            status=ProjectStatus.ACTIVE,
        )

        entity = map_create_request_to_entity(payload, owner_id)

        assert isinstance(entity, ProjectEntity)
        assert entity.name == "New Project"
        assert entity.description == "Some description"
        assert str(entity.owner_id) == owner_id
        assert entity.status == ProjectStatus.ACTIVE
        assert entity.id is not None

    def test_strips_whitespace_from_name(self):
        """Should strip leading/trailing whitespace from name."""
        payload = ProjectCreateRequest(name="  Spaced Name  ", description="desc")
        entity = map_create_request_to_entity(payload, str(uuid4()))

        assert entity.name == "Spaced Name"

    def test_strips_whitespace_from_description(self):
        """Should strip whitespace from description."""
        payload = ProjectCreateRequest(name="Name", description="  spaced desc  ")
        entity = map_create_request_to_entity(payload, str(uuid4()))

        assert entity.description == "spaced desc"

    def test_handles_none_description(self):
        """Should handle None description gracefully."""
        payload = ProjectCreateRequest(name="Name", description=None)
        entity = map_create_request_to_entity(payload, str(uuid4()))

        assert entity.description == ""

    def test_defaults_status_to_active(self):
        """Should default status to ACTIVE when not provided."""
        payload = ProjectCreateRequest(name="Name")
        entity = map_create_request_to_entity(payload, str(uuid4()))

        assert entity.status == ProjectStatus.ACTIVE

    def test_uses_provided_status(self):
        """Should use the status from the request."""
        payload = ProjectCreateRequest(
            name="Name",
            status=ProjectStatus.COMPLETED,
        )
        entity = map_create_request_to_entity(payload, str(uuid4()))

        assert entity.status == ProjectStatus.COMPLETED

    def test_invalid_owner_id_raises(self):
        """Should raise ValueError for invalid UUID format."""
        payload = ProjectCreateRequest(name="Name")

        with pytest.raises(ValueError):
            map_create_request_to_entity(payload, "not-a-uuid")
