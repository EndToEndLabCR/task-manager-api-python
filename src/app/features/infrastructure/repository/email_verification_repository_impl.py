from typing import Optional

import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.domain.entities.email_verification_entity import EmailVerificationEntity
from src.app.features.domain.repositories.email_verification_repository import EmailVerificationRepository
from src.app.features.infrastructure.models.email_verification_model import EmailVerificationTokenModel
from src.app.features.infrastructure.repository.email_verification_model_mapper import map_model_to_entity
from src.shared.utils.log_util import log


class DatabaseConnectionError(Exception):
    pass


class EmailVerificationRepositoryImpl(EmailVerificationRepository):

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, entity: EmailVerificationEntity) -> EmailVerificationEntity:
        try:
            log.info(f"[save] persisting email verification token for user_id: {entity.user_id}")

            model = EmailVerificationTokenModel(
                id=entity.id.value,
                user_id=entity.user_id,
                token_hash=entity.token_hash,
                expires_at=entity.expires_at,
                used_at=entity.used_at,
            )

            self.db_session.add(model)
            await self.db_session.commit()
            await self.db_session.refresh(model)

            log.info(f"[save] email verification token persisted. id={model.id}")
            return map_model_to_entity(model)

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(f"[save] DB connection error: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[save] Unexpected error: {str(e)}")
            raise

    async def find_by_token_hash(self, token_hash: str) -> Optional[EmailVerificationEntity]:
        try:
            result = await self.db_session.execute(
                select(EmailVerificationTokenModel).where(
                    EmailVerificationTokenModel.token_hash == token_hash
                )
            )
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return map_model_to_entity(model)

        except sqlalchemy.exc.OperationalError as db_error:
            log.error(f"[find_by_token_hash] DB connection error: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            log.error(f"[find_by_token_hash] Unexpected error: {str(e)}")
            raise

    async def update(self, entity: EmailVerificationEntity) -> Optional[EmailVerificationEntity]:
        try:
            model: Optional[EmailVerificationTokenModel] = await self.db_session.get(
                EmailVerificationTokenModel,
                entity.id.value,
            )

            if model is None:
                return None

            model.token_hash = entity.token_hash
            model.expires_at = entity.expires_at
            model.used_at = entity.used_at

            await self.db_session.commit()
            await self.db_session.refresh(model)

            return map_model_to_entity(model)

        except sqlalchemy.exc.OperationalError as db_error:
            await self.db_session.rollback()
            log.error(f"[update] DB connection error: {str(db_error)}")
            raise DatabaseConnectionError("Failed to connect to the database.") from db_error

        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[update] Unexpected error: {str(e)}")
            raise
