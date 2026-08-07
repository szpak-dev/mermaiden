from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class Task(Entity):
    kind: ClassVar[str] = "task"
    assigned: str = ""
    ticket: str = ""
    priority: str = ""


@dataclass(frozen=True, slots=True)
class Column(Container):
    kind: ClassVar[str] = "column"
