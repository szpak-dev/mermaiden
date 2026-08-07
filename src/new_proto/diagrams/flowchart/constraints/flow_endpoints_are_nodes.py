from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..elements import FlowNode
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="flow_endpoints_are_nodes")
class FlowEndpointsAreNodes(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.flow_endpoint"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

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
