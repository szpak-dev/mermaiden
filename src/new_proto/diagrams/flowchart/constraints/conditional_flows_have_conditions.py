from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import ConstraintLevel, Violation
from ....core.diagram import Diagram
from ..relations import ConditionalFlow
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="conditional_flows_have_conditions")
@dataclass(frozen=True, slots=True)
class ConditionalFlowsHaveConditions(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.conditional_flow_condition"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Conditional flow '{flow.id}' requires a condition.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if isinstance(flow, ConditionalFlow) and not flow.condition.strip()
        )
