from new_proto.interface import Interface

from ...core.diagram import Diagram
from ...core.element import Container, Entity
from ...core.relation import DirectedRelation


class FlowNode(Entity):
    pass


class FlowNodeGroup(Entity, Container):
    @Interface.prop
    def children(self) -> tuple[FlowNode, ...]: ...


class Flow(DirectedRelation):
    @Interface.prop
    def source(self) -> FlowNode: ...

    @Interface.prop
    def target(self) -> FlowNode: ...


class FlowchartDiagram(Diagram):
    @Interface.prop
    def elements(self) -> tuple[FlowNode | FlowNodeGroup, ...]: ...

    @Interface.prop
    def relations(self) -> tuple[Flow, ...]: ...
