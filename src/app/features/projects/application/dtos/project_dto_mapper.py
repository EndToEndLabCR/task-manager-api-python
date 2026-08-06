from src.app.features.projects.application.dtos.project_dto import (
    ProjectCreateRequest,
    ProjectResponse,
)
from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.shared.domain.value_objects.entity_id import EntityId


def map_entity_to_response(entity: ProjectEntity) -> ProjectResponse:
    """Convert a ProjectEntity to a ProjectResponse DTO.

    Args:
        entity: The project domain entity to convert.

    Returns:
        A ProjectResponse DTO with the entity's data.
    """
    return ProjectResponse(
        id=str(entity.id),
        name=entity.name,
        description=entity.description,
        owner_id=str(entity.owner_id),
        status=entity.status,
        github_repo_url=entity.github_repo_url,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def map_create_request_to_entity(payload: ProjectCreateRequest, owner_id: str) -> ProjectEntity:
    """Convert a ProjectCreateRequest DTO and owner ID to a ProjectEntity.

    Args:
        payload: The creation request DTO with project data.
        owner_id: The string ID of the project owner.

    Returns:
        A new ProjectEntity ready to be persisted.
    """
    return ProjectEntity(
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else "",
        owner_id=EntityId.from_string(owner_id),
        status=payload.status or ProjectStatus.ACTIVE,
        github_repo_url=payload.github_repo_url.strip() if payload.github_repo_url else None,
    )
