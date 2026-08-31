from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..elements import FlowNode
from .domain import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="flow_endpoints_are_nodes")
class FlowEndpointsAreNodes(FlowchartConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements()}
        return tuple(
            self.violation(
                f"Flow '{flow.id}' endpoints must both be flow nodes.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if len(flow.element_ids) == 2
            if flow.source_id in elements
            and flow.target_id in elements
            and not (isinstance(elements[flow.source_id], FlowNode) and isinstance(elements[flow.target_id], FlowNode))
        )
