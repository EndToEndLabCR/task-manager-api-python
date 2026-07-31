from typing import Optional
from sqlalchemy import select
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.application.exceptions.user_exception import UserAlreadyExistsException
from src.app.features.domain.entities.user_entity import UserEntity
from src.app.features.domain.repositories.user_repository import UserRepository
from src.app.features.domain.value_objects.email import Email
from src.app.features.infrastructure.models.user_model import UserModel
from src.app.features.infrastructure.repository.user_model_mapper import map_model_to_entity
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class DatabaseConnectionError(Exception):
    """Custom exception to indicate database connection errors."""
    pass


class UserRepositoryImpl(UserRepository):

    def __init__(self, db_session: AsyncSession):
        """
        Initializes the UserRepositoryImpl with a SQLAlchemy AsyncSession.

        Args:
            db_session (AsyncSession): The SQLAlchemy session to use for database operations.
        """
        self.db_session = db_session

    async def find_by_id(self, entity_id: EntityId) -> Optional[UserEntity]:

        try:
            log.info(f"start get user by id: {entity_id.value}")
            user_model: Optional[UserModel] = await self.db_session.get(UserModel, entity_id.value)

            if user_model is None:
                log.info(f"user by id {entity_id.value} not found")
                return None

            log.info(f"completed get user by id {entity_id.value}")

            return map_model_to_entity(user_model)

        except sqlalchemy.exc.OperationalError as db_error:
            log.error(f"Database connection error while finding user by id: {entity_id.value}. Error: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            log.error(f"Error finding user by id: {entity_id.value} Exceptions: {str(e)}")
            raise

    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        result = await self.db_session.execute(select(UserModel).where(UserModel.email == email.value))

        user_model = result.scalar_one_or_none()

        if user_model is None:
            log.info(f"User with email {email.value} not found.")
            return None

        log.info(f"User with email {email.value} found.")
        return map_model_to_entity(user_model)

    async def find_by_username(self, username: str) -> Optional[UserEntity]:
        result = await self.db_session.execute(select(UserModel).where(UserModel.username == username))

        user_model = result.scalar_one_or_none()

        if user_model is None:
            log.info(f"User with username {username} not found.")
            return None

        log.info(f"User with username {username} found.")
        return map_model_to_entity(user_model)

    async def save(self, user: UserEntity) -> UserEntity:
        try:
            result = await self.db_session.execute(select(UserModel).where(UserModel.email == user.email.value))

            if result.scalar_one_or_none():
                log.warning(f"[save] User with email {user.email} already exists")
                raise UserAlreadyExistsException(user.email.value)

            log.info("[create_user] about to persist user")

            user_model = UserModel(
                id=user.id.value,
                email=user.email.value,
                username=user.username,
                password_hash=user.password_hash,
                preferences=user.preferences
            )

            self.db_session.add(user_model)
            await self.db_session.commit()
            await self.db_session.refresh(user_model)

            log.info(f"[save] User persisted successfully. id={user_model.id}")
            return map_model_to_entity(user_model)

        except sqlalchemy.exc.IntegrityError as e:
            await self.db_session.rollback()

            log.error(f"[save] IntegrityError while saving user with email {user.email}: {e}")
            raise UserAlreadyExistsException(user.email.value) from e

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[save] Unexpected error while saving user with email {user.email}: {e}")
            raise

    async def update(self, entity: UserEntity) -> Optional[UserEntity]:
        try:
            log.info(f"[update] start update user id: {entity.id.value}")

            user_model: Optional[UserModel] = await self.db_session.get(
                UserModel,
                entity.id.value
            )

            if user_model is None:
                log.info(f"[update] user by id {entity.id.value} not found")
                return None

            user_model.email = entity.email.value
            user_model.username = entity.username
            user_model.password_hash = entity.password_hash

            if hasattr(entity, "preferences"):
                user_model.preferences = entity.preferences

            await self.db_session.commit()
            await self.db_session.refresh(user_model)

            log.info(f"[update] completed update user id: {entity.id.value}")
            return map_model_to_entity(user_model)

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(
                f"Database connection error while updating user by id: {entity.id.value}. Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"Error updating user by id: {entity.id.value}. Error: {str(e)}")
            raise

    async def delete(self, entity_id: EntityId) -> bool:
        try:
            log.info(f"start delete user by id: {entity_id.value}")
            user_model: Optional[UserModel] = await self.db_session.get(UserModel, entity_id.value)

            if user_model is None:
                log.info(f"user by id {entity_id.value} not found for deletion")
                return False

            await self.db_session.delete(user_model)
            await self.db_session.commit()

            log.info(f"completed delete user by id {entity_id.value}")
            return True

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(
                f"Database connection error while deleting user by id: {entity_id.value}. Error: {str(db_error)}"
            )
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"Error deleting user by id: {entity_id.value}. Error: {str(e)}")
            raise