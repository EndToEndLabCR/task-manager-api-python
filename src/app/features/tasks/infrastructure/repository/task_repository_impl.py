from typing import List, Optional

import sqlalchemy.exc
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.tasks.domain.entities.task_entity import TaskEntity
from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.domain.entities.task_status import TaskStatus
from src.app.features.tasks.domain.repositories.task_repository import TaskRepository
from src.app.features.tasks.infrastructure.models.task_model import TaskModel
from src.app.features.tasks.infrastructure.repository.task_model_mapper import map_model_to_entity
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class DatabaseConnectionError(Exception):
    pass


class TaskRepositoryImpl(TaskRepository):

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, entity: TaskEntity) -> TaskEntity:
        try:
            model = TaskModel(
                id=entity.id.value,
                project_id=entity.project_id.value,
                title=entity.title,
                description=entity.description,
                status=entity.status.value,
                priority=entity.priority.value,
                source_note_id=entity.source_note_id.value if entity.source_note_id else None,
            )
            self.db_session.add(model)
            await self.db_session.commit()
            await self.db_session.refresh(model)
            return map_model_to_entity(model)
        except sqlalchemy.exc.IntegrityError as e:
            await self.db_session.rollback()
            log.error(f"[TaskRepo.save] IntegrityError: {e}")
            raise
        except sqlalchemy.exc.OperationalError as e:
            await self.db_session.rollback()
            raise DatabaseConnectionError("Failed to connect to the database.") from e
        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[TaskRepo.save] Unexpected error: {e}")
            raise

    async def find_by_id(self, entity_id: EntityId) -> Optional[TaskEntity]:
        try:
            model = await self.db_session.get(TaskModel, entity_id.value)
            return map_model_to_entity(model) if model else None
        except sqlalchemy.exc.OperationalError as e:
            raise DatabaseConnectionError("Failed to connect to the database.") from e

    async def find_all_by_project_id(
        self,
        project_id: EntityId,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        page: int = 1,
        size: int = 50,
    ) -> List[TaskEntity]:
        try:
            stmt = select(TaskModel).where(TaskModel.project_id == project_id.value)
            if status is not None:
                stmt = stmt.where(TaskModel.status == status.value)
            if priority is not None:
                stmt = stmt.where(TaskModel.priority == priority.value)
            stmt = stmt.order_by(TaskModel.created_at.desc())
            stmt = stmt.offset((page - 1) * size).limit(size)
            result = await self.db_session.execute(stmt)
            return [map_model_to_entity(m) for m in result.scalars().all()]
        except sqlalchemy.exc.OperationalError as e:
            raise DatabaseConnectionError("Failed to connect to the database.") from e

    async def count_by_project_id(
        self,
        project_id: EntityId,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> int:
        try:
            stmt = select(func.count()).select_from(TaskModel).where(TaskModel.project_id == project_id.value)
            if status is not None:
                stmt = stmt.where(TaskModel.status == status.value)
            if priority is not None:
                stmt = stmt.where(TaskModel.priority == priority.value)
            result = await self.db_session.execute(stmt)
            return result.scalar_one()
        except sqlalchemy.exc.OperationalError as e:
            raise DatabaseConnectionError("Failed to connect to the database.") from e

    async def update(self, entity: TaskEntity) -> Optional[TaskEntity]:
        try:
            model = await self.db_session.get(TaskModel, entity.id.value)
            if model is None:
                return None
            model.title = entity.title
            model.description = entity.description
            model.status = entity.status.value
            model.priority = entity.priority.value
            model.source_note_id = entity.source_note_id.value if entity.source_note_id else None
            await self.db_session.commit()
            await self.db_session.refresh(model)
            return map_model_to_entity(model)
        except sqlalchemy.exc.OperationalError as e:
            await self.db_session.rollback()
            raise DatabaseConnectionError("Failed to connect to the database.") from e
        except Exception as e:
            await self.db_session.rollback()
            log.error(f"[TaskRepo.update] Error: {e}")
            raise

    async def delete(self, entity_id: EntityId) -> bool:
        try:
            model = await self.db_session.get(TaskModel, entity_id.value)
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
            log.error(f"[TaskRepo.delete] Error: {e}")
            raise
