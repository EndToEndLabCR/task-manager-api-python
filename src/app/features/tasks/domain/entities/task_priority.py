from enum import Enum


class TaskPriority(str, Enum):
    """Priority level of a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
