from new_proto.interface import Interface

from ...core.diagram import Diagram
from .elements import FlowNode, FlowNodeGroup
from .relations import Flow


class FlowchartDiagram(Diagram):
    @Interface.prop
    def elements(self) -> tuple[FlowNode | FlowNodeGroup, ...]: ...

    @Interface.prop
    def relations(self) -> tuple[Flow, ...]: ...
