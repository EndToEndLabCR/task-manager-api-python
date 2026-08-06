from enum import Enum


class NoteType(str, Enum):
    """Enum representing the possible types/states of a project note."""

    RAW = "raw"
    TASK = "task"
    ARCHITECTURE_DECISION = "architecture_decision"
