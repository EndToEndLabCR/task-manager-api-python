from enum import Enum


class TaskStatus(str, Enum):
    """Lifecycle status of a task."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
