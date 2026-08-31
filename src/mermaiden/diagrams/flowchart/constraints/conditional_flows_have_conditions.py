from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..relations import ConditionalFlow
from .domain import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="conditional_flows_have_conditions")
class ConditionalFlowsHaveConditions(FlowchartConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Conditional flow '{flow.id}' requires a condition.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if isinstance(flow, ConditionalFlow) and not flow.condition.strip()
        )
