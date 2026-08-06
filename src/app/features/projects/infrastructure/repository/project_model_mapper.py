from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.entities.project_status import ProjectStatus
from src.app.features.projects.infrastructure.models.project_model import ProjectModel
from src.shared.domain.value_objects.entity_id import EntityId


def map_model_to_entity(project_model: ProjectModel) -> ProjectEntity:
    """Maps a ProjectModel (SQLAlchemy) to a ProjectEntity (domain).

    Args:
        project_model: The SQLAlchemy model instance to map.

    Returns:
        A ProjectEntity domain object.
    """
    return ProjectEntity(
        id=EntityId(project_model.id),
        name=project_model.name,
        description=project_model.description,
        owner_id=EntityId(project_model.owner_id),
        status=ProjectStatus(project_model.status),
        github_repo_url=project_model.github_repo_url,
        created_at=project_model.created_at,
        updated_at=project_model.updated_at,
    )
