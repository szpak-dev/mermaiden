from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..elements import SwimlaneNode
from .domain import SwimlaneConstraint


@injectable(as_type=SwimlaneConstraint, qualifier="flow_endpoints_are_nodes")
class FlowEndpointsAreNodes(SwimlaneConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements("")}
        return tuple(
            self.violation(
                f"Flow '{flow.id}' endpoints must both be swimlane nodes.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if len(flow.element_ids) == 2
            if flow.source_id in elements
            and flow.target_id in elements
            and not (
                isinstance(elements[flow.source_id], SwimlaneNode)
                and isinstance(elements[flow.target_id], SwimlaneNode)
            )
        )
