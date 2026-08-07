from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class Task(Entity):
    kind: ClassVar[str] = "task"
    metadata: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Milestone(Entity):
    kind: ClassVar[str] = "milestone"
    metadata: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Marker(Entity):
    kind: ClassVar[str] = "marker"
    date: str = ""


@dataclass(frozen=True, slots=True)
class Section(Container):
    kind: ClassVar[str] = "section"
