from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class EventModelingElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in Event Modeling diagram"


@dataclass(frozen=True, slots=True)
class Event(Entity, EventModelingElementMember):
    kind: ClassVar[str] = "event"


@dataclass(frozen=True, slots=True)
class Command(Entity, EventModelingElementMember):
    kind: ClassVar[str] = "command"


@dataclass(frozen=True, slots=True)
class View(Entity, EventModelingElementMember):
    kind: ClassVar[str] = "view"


@dataclass(frozen=True, slots=True)
class Actor(Entity, EventModelingElementMember):
    kind: ClassVar[str] = "actor"


@dataclass(frozen=True, slots=True)
class Swimlane(Container, EventModelingElementMember):
    kind: ClassVar[str] = "swimlane"

