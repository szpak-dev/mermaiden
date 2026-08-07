from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="flows_are_binary")
class FlowsAreBinary(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.binary_flow"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Flow '{flow.id}' requires exactly one source and one target.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if len(flow.element_ids) != 2
        )
