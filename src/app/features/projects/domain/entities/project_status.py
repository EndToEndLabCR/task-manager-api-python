from enum import Enum


class ProjectStatus(str, Enum):
    """Enum representing the possible statuses of a project."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"
