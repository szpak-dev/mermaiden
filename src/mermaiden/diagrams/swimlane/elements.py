from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class Swimlane(Container):
    kind: ClassVar[str] = "swimlane"


@dataclass(frozen=True, slots=True)
class SwimlaneNode(Entity):
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
