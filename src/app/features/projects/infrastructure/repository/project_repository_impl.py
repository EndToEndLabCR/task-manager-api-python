from typing import Optional, List

from sqlalchemy import select
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.projects.domain.entities.project_entity import ProjectEntity
from src.app.features.projects.domain.repositories.project_repository import ProjectRepository
from src.app.features.projects.infrastructure.models.project_model import ProjectModel
from src.app.features.projects.infrastructure.repository.project_model_mapper import map_model_to_entity
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class DatabaseConnectionError(Exception):
    """Custom exception to indicate database connection errors."""
    pass


class ProjectRepositoryImpl(ProjectRepository):

    def __init__(self, db_session: AsyncSession):
        """
        Initializes the ProjectRepositoryImpl with a SQLAlchemy AsyncSession.

        Args:
            db_session (AsyncSession): The SQLAlchemy session to use for database operations.
        """
        self.db_session = db_session

    async def save(self, entity: ProjectEntity) -> ProjectEntity:
        """Persists a new project entity to the database.

        Args:
            entity: The ProjectEntity to save.

        Returns:
            The persisted ProjectEntity with updated timestamps.

        Raises:
            DatabaseConnectionError: If there is a database connectivity issue.
        """
        try:
            log.info(f"[save] about to persist project with name: {entity.name}")

            project_model = ProjectModel(
                id=entity.id.value,
                name=entity.name,
                description=entity.description,
                owner_id=entity.owner_id.value,
                status=entity.status.value.lower(),
                github_repo_url=entity.github_repo_url,
            )

            self.db_session.add(project_model)
            await self.db_session.commit()
            await self.db_session.refresh(project_model)

            log.info(f"[save] Project persisted successfully. id={project_model.id}")
            return map_model_to_entity(project_model)

        except sqlalchemy.exc.IntegrityError as e:
            await self.db_session.rollback()
            log.error(f"[save] IntegrityError while saving project: {e}")
            raise

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(f"[save] Database connection error while saving project: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[save] Unexpected error while saving project: {e}")
            raise

    async def find_by_id(self, entity_id: EntityId) -> Optional[ProjectEntity]:
        """Finds a project by its unique identifier.

        Args:
            entity_id: The EntityId of the project to find.

        Returns:
            The ProjectEntity if found, None otherwise.

        Raises:
            DatabaseConnectionError: If there is a database connectivity issue.
        """
        try:
            log.info(f"[find_by_id] start get project by id: {entity_id.value}")
            project_model: Optional[ProjectModel] = await self.db_session.get(ProjectModel, entity_id.value)

            if project_model is None:
                log.info(f"[find_by_id] project by id {entity_id.value} not found")
                return None

            log.info(f"[find_by_id] completed get project by id {entity_id.value}")
            return map_model_to_entity(project_model)

        except sqlalchemy.exc.OperationalError as db_error:
            log.error(
                f"[find_by_id] Database connection error while finding project by id: {entity_id.value}. "
                f"Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            log.error(f"[find_by_id] Error finding project by id: {entity_id.value}. Error: {str(e)}")
            raise

    async def find_all_by_owner_id(self, owner_id: EntityId) -> List[ProjectEntity]:
        """Finds all projects belonging to a specific owner.

        Args:
            owner_id: The EntityId of the owner.

        Returns:
            A list of ProjectEntity objects owned by the specified user.

        Raises:
            DatabaseConnectionError: If there is a database connectivity issue.
        """
        try:
            log.info(f"[find_all_by_owner_id] start get projects for owner: {owner_id.value}")

            result = await self.db_session.execute(
                select(ProjectModel).where(ProjectModel.owner_id == owner_id.value)
            )
            project_models = result.scalars().all()

            log.info(
                f"[find_all_by_owner_id] found {len(project_models)} projects for owner: {owner_id.value}"
            )
            return [map_model_to_entity(model) for model in project_models]

        except sqlalchemy.exc.OperationalError as db_error:
            log.error(
                f"[find_all_by_owner_id] Database connection error while finding projects for owner: "
                f"{owner_id.value}. Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            log.error(
                f"[find_all_by_owner_id] Error finding projects for owner: {owner_id.value}. Error: {str(e)}"
            )
            raise

    async def exists_by_owner_id_and_name(
        self, owner_id: EntityId, name: str, exclude_id: Optional[EntityId] = None
    ) -> bool:
        """Checks whether the owner already has a project with the given name.

        Args:
            owner_id: The EntityId of the owner.
            name: The project name to check.
            exclude_id: Optional project id to exclude (for updates).

        Returns:
            True if a project with that name already exists for the owner.

        Raises:
            DatabaseConnectionError: If there is a database connectivity issue.
        """
        try:
            query = select(ProjectModel.id).where(
                ProjectModel.owner_id == owner_id.value,
                ProjectModel.name == name,
            )
            if exclude_id is not None:
                query = query.where(ProjectModel.id != exclude_id.value)

            result = await self.db_session.execute(query.limit(1))
            return result.scalar_one_or_none() is not None

        except sqlalchemy.exc.OperationalError as db_error:
            log.error(
                f"[exists_by_owner_id_and_name] Database connection error for owner: "
                f"{owner_id.value}. Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            log.error(
                f"[exists_by_owner_id_and_name] Error checking project name for owner: "
                f"{owner_id.value}. Error: {str(e)}"
            )
            raise

    async def update(self, entity: ProjectEntity) -> Optional[ProjectEntity]:
        """Updates an existing project entity in the database.

        Args:
            entity: The ProjectEntity with updated fields.

        Returns:
            The updated ProjectEntity if found and updated, None if not found.

        Raises:
            DatabaseConnectionError: If there is a database connectivity issue.
        """
        try:
            log.info(f"[update] start update project id: {entity.id.value}")

            project_model: Optional[ProjectModel] = await self.db_session.get(
                ProjectModel, entity.id.value
            )

            if project_model is None:
                log.info(f"[update] project by id {entity.id.value} not found")
                return None

            project_model.name = entity.name
            project_model.description = entity.description
            project_model.status = entity.status.value.lower()
            project_model.github_repo_url = entity.github_repo_url

            await self.db_session.commit()
            await self.db_session.refresh(project_model)

            log.info(f"[update] completed update project id: {entity.id.value}")
            return map_model_to_entity(project_model)

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(
                f"[update] Database connection error while updating project by id: {entity.id.value}. "
                f"Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except sqlalchemy.exc.IntegrityError as e:
            await self.db_session.rollback()
            log.error(f"[update] IntegrityError while updating project id {entity.id.value}: {e}")
            raise

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[update] Error updating project by id: {entity.id.value}. Error: {str(e)}")
            raise

    async def delete(self, entity_id: EntityId) -> bool:
        """Deletes a project by its unique identifier.

        Args:
            entity_id: The EntityId of the project to delete.

        Returns:
            True if the project was deleted, False if not found.

        Raises:
            DatabaseConnectionError: If there is a database connectivity issue.
        """
        try:
            log.info(f"[delete] start delete project by id: {entity_id.value}")
            project_model: Optional[ProjectModel] = await self.db_session.get(ProjectModel, entity_id.value)

            if project_model is None:
                log.info(f"[delete] project by id {entity_id.value} not found for deletion")
                return False

            await self.db_session.delete(project_model)
            await self.db_session.commit()

            log.info(f"[delete] completed delete project by id {entity_id.value}")
            return True

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(
                f"[delete] Database connection error while deleting project by id: {entity_id.value}. "
                f"Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[delete] Error deleting project by id: {entity_id.value}. Error: {str(e)}")
            raise
