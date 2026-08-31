from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from .domain import SwimlaneConstraint


@injectable(as_type=SwimlaneConstraint, qualifier="flows_are_binary")
class FlowsAreBinary(SwimlaneConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Flow '{flow.id}' requires exactly one source and one target.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if len(flow.element_ids) != 2
        )
