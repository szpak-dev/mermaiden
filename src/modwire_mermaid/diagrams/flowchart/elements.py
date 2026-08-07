from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.element import Container, Entity


class Direction(StrEnum):
    TOP_DOWN = "TD"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"
    BOTTOM_UP = "BT"


@dataclass(frozen=True, slots=True)
class FlowNode(Entity):
    kind: ClassVar[str] = "flow_node"


@dataclass(frozen=True, slots=True)
class Start(FlowNode):
    kind: ClassVar[str] = "start"


@dataclass(frozen=True, slots=True)
class End(FlowNode):
    kind: ClassVar[str] = "end"


@dataclass(frozen=True, slots=True)
class Action(FlowNode):
    kind: ClassVar[str] = "action"


@dataclass(frozen=True, slots=True)
class Decision(FlowNode):
    kind: ClassVar[str] = "decision"


@dataclass(frozen=True, slots=True)
class InputOutput(FlowNode):
    kind: ClassVar[str] = "input_output"


@dataclass(frozen=True, slots=True)
class DataStore(FlowNode):
    kind: ClassVar[str] = "data_store"


@dataclass(frozen=True, slots=True)
class Document(FlowNode):
    kind: ClassVar[str] = "document"


@dataclass(frozen=True, slots=True)
class Subprocess(FlowNode):
    kind: ClassVar[str] = "subprocess"


@dataclass(frozen=True, slots=True)
class Junction(FlowNode):
    kind: ClassVar[str] = "junction"


@dataclass(frozen=True, slots=True)
class FlowGroup(Container):
    kind: ClassVar[str] = "flow_group"
    direction: Direction | None = None
