from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class SwimlaneElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a swimlane diagram"


@dataclass(frozen=True, slots=True)
class Swimlane(Container, SwimlaneElementMember):
    kind: ClassVar[str] = "swimlane"


@dataclass(frozen=True, slots=True)
class SwimlaneNode(Entity, SwimlaneElementMember):
    kind: ClassVar[str] = "swimlane_node"


@dataclass(frozen=True, slots=True)
class Activity(SwimlaneNode):
    kind: ClassVar[str] = "activity"


@dataclass(frozen=True, slots=True)
class Start(SwimlaneNode):
    kind: ClassVar[str] = "start"


@dataclass(frozen=True, slots=True)
class End(SwimlaneNode):
    kind: ClassVar[str] = "end"


@dataclass(frozen=True, slots=True)
class Decision(SwimlaneNode):
    kind: ClassVar[str] = "decision"


@dataclass(frozen=True, slots=True)
class Connector(SwimlaneNode):
    kind: ClassVar[str] = "connector"
