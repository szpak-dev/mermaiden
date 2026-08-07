from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class Event(Entity):
    kind: ClassVar[str] = "event"


@dataclass(frozen=True, slots=True)
class Command(Entity):
    kind: ClassVar[str] = "command"


@dataclass(frozen=True, slots=True)
class View(Entity):
    kind: ClassVar[str] = "view"


@dataclass(frozen=True, slots=True)
class Actor(Entity):
    kind: ClassVar[str] = "actor"


@dataclass(frozen=True, slots=True)
class Swimlane(Container):
    kind: ClassVar[str] = "swimlane"

