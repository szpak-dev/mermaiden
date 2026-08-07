from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class GanttElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a Gantt chart"


@dataclass(frozen=True, slots=True)
class Task(Entity, GanttElementMember):
    kind: ClassVar[str] = "task"
    metadata: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Milestone(Entity, GanttElementMember):
    kind: ClassVar[str] = "milestone"
    metadata: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Marker(Entity, GanttElementMember):
    kind: ClassVar[str] = "marker"
    date: str = ""


@dataclass(frozen=True, slots=True)
class Section(Container, GanttElementMember):
    kind: ClassVar[str] = "section"
