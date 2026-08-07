from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from ..elements import Start
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="exactly_one_start")
class ExactlyOneStart(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.one_start"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        count = sum(isinstance(item, Start) for item in diagram.walk_elements())
        if count == 1:
            return ()
        return (self.violation(f"Flowchart requires exactly one start; found {count}."),)
