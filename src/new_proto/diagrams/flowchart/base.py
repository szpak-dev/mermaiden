from ...core.diagram import Diagram
from ...core.element import Container, Entity
from ...core.relation import DirectedRelation


class FlowNode(Entity):
    pass


class FlowNodeGroup(Entity, Container):
    children: tuple[FlowNode, ...]


class Flow(DirectedRelation):
    source: FlowNode
    target: FlowNode


class Flowchart(Diagram):
    elements: tuple[FlowNode | FlowNodeGroup, ...]
    relations: tuple[Flow, ...]
