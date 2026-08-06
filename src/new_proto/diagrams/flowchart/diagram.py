from new_proto.interface import Interface

from ...core.diagram import Diagram
from .elements import FlowGroup, FlowNode
from .relations import ConditionalFlow, Flow, ParallelRegion


class Flowchart(Diagram):
    @Interface.method
    def add_node(self, node: FlowNode, *, group: FlowGroup | None = None) -> None: ...

    @Interface.method
    def add_group(self, group: FlowGroup) -> None: ...

    @Interface.method
    def add_flow(self, flow: Flow) -> None: ...

    @Interface.method
    def add_conditional_flow(self, flow: ConditionalFlow) -> None: ...

    @Interface.method
    def add_parallel_region(self, region: ParallelRegion) -> None: ...
