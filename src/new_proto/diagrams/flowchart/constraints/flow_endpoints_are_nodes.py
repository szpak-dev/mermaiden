from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import Violation
from ....core.diagram import Diagram
from ..elements.elements import FlowNode
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="flow_endpoints_are_nodes")
@dataclass(frozen=True, slots=True)
class FlowEndpointsAreNodes(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.flow_endpoint"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.elements}
        return tuple(
            self.violation(
                f"Flow '{flow.id}' endpoints must both be flow nodes.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if flow.source_id in elements
            and flow.target_id in elements
            and not (
                isinstance(elements[flow.source_id], FlowNode)
                and isinstance(elements[flow.target_id], FlowNode)
            )
        )
