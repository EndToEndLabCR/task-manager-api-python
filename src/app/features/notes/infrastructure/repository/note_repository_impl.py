from typing import List, Optional

import sqlalchemy.exc
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.notes.domain.entities.note_entity import NoteEntity
from src.app.features.notes.domain.entities.note_type import NoteType
from src.app.features.notes.domain.repositories.note_repository import NoteRepository
from src.app.features.notes.infrastructure.models.note_model import NoteModel
from src.app.features.notes.infrastructure.repository.note_model_mapper import map_model_to_entity
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class DatabaseConnectionError(Exception):
    pass


class NoteRepositoryImpl(NoteRepository):

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, entity: NoteEntity) -> NoteEntity:
        try:
            model = NoteModel(
                id=entity.id.value,
                project_id=entity.project_id.value,
                content=entity.content,
                note_type=entity.note_type.value,
                is_enriched=entity.is_enriched,
                ai_suggestion=entity.ai_suggestion,
            )
            self.db_session.add(model)
            await self.db_session.commit()
            await self.db_session.refresh(model)
            return map_model_to_entity(model)
        except sqlalchemy.exc.IntegrityError as e:
            await self.db_session.rollback()
            log.error(f"[NoteRepo.save] IntegrityError: {e}")
            raise
        except sqlalchemy.exc.OperationalError as e:
            await self.db_session.rollback()
            raise DatabaseConnectionError("Failed to connect to the database.") from e
        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[NoteRepo.save] Unexpected error: {e}")
            raise

    async def find_by_id(self, entity_id: EntityId) -> Optional[NoteEntity]:
        try:
            model = await self.db_session.get(NoteModel, entity_id.value)
            return map_model_to_entity(model) if model else None
        except sqlalchemy.exc.OperationalError as e:
            raise DatabaseConnectionError("Failed to connect to the database.") from e

    async def find_all_by_project_id(
        self,
        project_id: EntityId,
        note_type: Optional[NoteType] = None,
        page: int = 1,
        size: int = 50,
    ) -> List[NoteEntity]:
        try:
            stmt = select(NoteModel).where(NoteModel.project_id == project_id.value)
            if note_type is not None:
                stmt = stmt.where(NoteModel.note_type == note_type.value)
            stmt = stmt.order_by(NoteModel.created_at.desc())
            stmt = stmt.offset((page - 1) * size).limit(size)
            result = await self.db_session.execute(stmt)
            return [map_model_to_entity(m) for m in result.scalars().all()]
        except sqlalchemy.exc.OperationalError as e:
            raise DatabaseConnectionError("Failed to connect to the database.") from e

    async def count_by_project_id(
        self,
        project_id: EntityId,
        note_type: Optional[NoteType] = None,
    ) -> int:
        try:
            stmt = select(func.count()).select_from(NoteModel).where(NoteModel.project_id == project_id.value)
            if note_type is not None:
                stmt = stmt.where(NoteModel.note_type == note_type.value)
            result = await self.db_session.execute(stmt)
            return result.scalar_one()
        except sqlalchemy.exc.OperationalError as e:
            raise DatabaseConnectionError("Failed to connect to the database.") from e

    async def update(self, entity: NoteEntity) -> Optional[NoteEntity]:
        try:
            model = await self.db_session.get(NoteModel, entity.id.value)
            if model is None:
                return None
            model.content = entity.content
            model.note_type = entity.note_type.value
            model.is_enriched = entity.is_enriched
            model.ai_suggestion = entity.ai_suggestion
            await self.db_session.commit()
            await self.db_session.refresh(model)
            return map_model_to_entity(model)
        except sqlalchemy.exc.OperationalError as e:
            await self.db_session.rollback()
            raise DatabaseConnectionError("Failed to connect to the database.") from e
        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[NoteRepo.update] Error: {e}")
            raise

    async def delete(self, entity_id: EntityId) -> bool:
        try:
            model = await self.db_session.get(NoteModel, entity_id.value)
            if model is None:
                return False
            await self.db_session.delete(model)
            await self.db_session.commit()
            return True
        except sqlalchemy.exc.OperationalError as e:
            await self.db_session.rollback()
            raise DatabaseConnectionError("Failed to connect to the database.") from e
        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[NoteRepo.delete] Error: {e}")
            raise
