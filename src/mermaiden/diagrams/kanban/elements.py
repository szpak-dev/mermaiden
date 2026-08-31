from enum import StrEnum

from ...core.domain import Container, Entity


class KanbanPriority(StrEnum):
    VERY_HIGH = "Very High"
    HIGH = "High"
    LOW = "Low"
    VERY_LOW = "Very Low"


class Task(Entity):
    assigned: str = ""
    ticket: str = ""
    priority: KanbanPriority | str = ""


class Column(Container):
    pass
