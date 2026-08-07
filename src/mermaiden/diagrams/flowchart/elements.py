from enum import StrEnum

from ...core.element import Container, Entity


class Direction(StrEnum):
    TOP_DOWN = "TD"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"
    BOTTOM_UP = "BT"


class FlowNode(Entity):
    pass


class Start(FlowNode):
    pass


class End(FlowNode):
    pass


class Action(FlowNode):
    pass


class Decision(FlowNode):
    pass


class InputOutput(FlowNode):
    pass


class DataStore(FlowNode):
    pass


class Document(FlowNode):
    pass


class Subprocess(FlowNode):
    pass


class Junction(FlowNode):
    pass


class FlowGroup(Container):
    direction: Direction | None = None
