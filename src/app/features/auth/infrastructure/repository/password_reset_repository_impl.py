# password_reset_repository_impl.py
from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy.exc
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.auth.domain.entities.password_reset_entity import PasswordResetEntity
from src.app.features.auth.domain.repositories.password_reset_repository import PasswordResetRepository
from src.app.features.auth.infrastructure.models.password_reset_model import PasswordResetTokenModel
from src.app.features.auth.infrastructure.repository.password_reset_model_mapper import map_model_to_entity
from src.shared.utils.log_util import log


class DatabaseConnectionError(Exception):
    """Custom exception to indicate database connection errors."""
    pass


class PasswordResetRepositoryImpl(PasswordResetRepository):

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def find_by_token_hash(self, token_hash: str) -> Optional[PasswordResetEntity]:
        try:
            log.info("[find_by_token_hash] start lookup by token hash")
            result = await self.db_session.execute(
                select(PasswordResetTokenModel).where(
                    PasswordResetTokenModel.token_hash == token_hash
                )
            )
            model = result.scalar_one_or_none()

            if model is None:
                log.info("[find_by_token_hash] token not found")
                return None

            log.info("[find_by_token_hash] token found")
            return map_model_to_entity(model)

        except sqlalchemy.exc.OperationalError as db_error:
            log.error(f"[find_by_token_hash] DB connection error: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            log.error(f"[find_by_token_hash] Unexpected error: {str(e)}")
            raise

    async def count_recent_requests(self, user_id: UUID, since: datetime) -> int:
        try:
            log.info(f"[count_recent_requests] counting requests for user_id: {user_id}")
            result = await self.db_session.execute(
                select(func.count()).select_from(PasswordResetTokenModel).where(
                    and_(
                        PasswordResetTokenModel.user_id == user_id,
                        PasswordResetTokenModel.created_at >= since,
                    )
                )
            )
            count = result.scalar() or 0
            log.info(f"[count_recent_requests] count: {count}")
            return count

        except sqlalchemy.exc.OperationalError as db_error:
            log.error(f"[count_recent_requests] DB connection error: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            log.error(f"[count_recent_requests] Unexpected error: {str(e)}")
            raise

    async def save(self, entity: PasswordResetEntity) -> PasswordResetEntity:
        try:
            log.info(f"[save] persisting reset token for user_id: {entity.user_id}")

            model = PasswordResetTokenModel(
                id=entity.id.value,
                user_id=entity.user_id,
                token_hash=entity.token_hash,
                expires_at=entity.expires_at,
                created_at=entity.created_at,
                used_at=entity.used_at,
            )

            self.db_session.add(model)
            await self.db_session.commit()
            await self.db_session.refresh(model)

            log.info(f"[save] reset token persisted successfully. id={model.id}")
            return map_model_to_entity(model)

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(f"[save] DB connection error: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[save] Unexpected error: {str(e)}")
            raise

    async def update(self, entity: PasswordResetEntity) -> Optional[PasswordResetEntity]:
        try:
            log.info(f"[update] start update reset token id: {entity.id}")

            model: Optional[PasswordResetTokenModel] = await self.db_session.get(
                PasswordResetTokenModel,
                entity.id.value,
            )

            if model is None:
                log.info(f"[update] reset token id {entity.id} not found")
                return None

            model.user_id = entity.user_id
            model.token_hash = entity.token_hash
            model.expires_at = entity.expires_at
            model.created_at = entity.created_at
            model.used_at = entity.used_at

            await self.db_session.commit()
            await self.db_session.refresh(model)

            log.info(f"[update] completed update reset token id: {entity.id}")
            return map_model_to_entity(model)

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(f"[update] DB connection error: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[update] Unexpected error: {str(e)}")
            raise