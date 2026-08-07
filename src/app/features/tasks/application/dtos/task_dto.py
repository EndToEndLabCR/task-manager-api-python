from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.app.features.tasks.domain.entities.task_priority import TaskPriority
from src.app.features.tasks.domain.entities.task_status import TaskStatus


class TaskCreateRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
    source_note_id: Optional[str] = Field(default=None)


class TaskUpdateRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=None)


class TaskResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: str
    project_id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    source_note_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: List[TaskResponse]
    total: int
    page: int
    size: int
