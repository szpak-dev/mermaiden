from dataclasses import dataclass
from enum import StrEnum

from ....core.element import Container, Entity


class Direction(StrEnum):
    TOP_DOWN = "TD"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"
    BOTTOM_UP = "BT"


@dataclass(frozen=True, slots=True)
class FlowNode(Entity):
    pass


@dataclass(frozen=True, slots=True)
class Start(FlowNode):
    pass


@dataclass(frozen=True, slots=True)
class End(FlowNode):
    pass


@dataclass(frozen=True, slots=True)
class Action(FlowNode):
    pass


@dataclass(frozen=True, slots=True)
class Decision(FlowNode):
    pass


@dataclass(frozen=True, slots=True)
class FlowGroup(Container):
    direction: Direction | None = None
