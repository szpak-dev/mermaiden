from dataclasses import dataclass
from enum import StrEnum

from ....core.element import Container, Element


class Direction(StrEnum):
    TOP_DOWN = "TD"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"
    BOTTOM_UP = "BT"


@dataclass(frozen=True, slots=True)
class FlowNode(Element):
    element_id: str
    label: str
    parent_id: str | None = None

    @property
    def id(self) -> str:
        return self.element_id

    @property
    def owner_id(self) -> str | None:
        return self.parent_id


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
    element_id: str
    label: str
    parent_id: str | None = None
    direction: Direction | None = None

    @property
    def id(self) -> str:
        return self.element_id

    @property
    def owner_id(self) -> str | None:
        return self.parent_id
