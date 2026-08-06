from ...runtime.diagram import InMemoryDiagram
from .diagram import Flowchart
from .elements import FlowGroup, FlowNode
from .relations import ConditionalFlow, Flow, ParallelRegion


class InMemoryFlowchart(InMemoryDiagram, Flowchart):
    def add_node(self, node: FlowNode, *, group: FlowGroup | None = None) -> None:
        self.add_element(node, owner=group)

    def add_group(self, group: FlowGroup) -> None:
        self.add_element(group)

    def add_flow(self, flow: Flow) -> None:
        self.add_relation(flow)

    def add_conditional_flow(self, flow: ConditionalFlow) -> None:
        self.add_relation(flow)

    def add_parallel_region(self, region: ParallelRegion) -> None:
        self.add_relation(region)
