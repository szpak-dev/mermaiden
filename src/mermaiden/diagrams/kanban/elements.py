from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class KanbanElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in Kanban diagram"


@dataclass(frozen=True, slots=True)
class Task(Entity, KanbanElementMember):
    kind: ClassVar[str] = "task"
    assigned: str = ""
    ticket: str = ""
    priority: str = ""


@dataclass(frozen=True, slots=True)
class Column(Container, KanbanElementMember):
    kind: ClassVar[str] = "column"
