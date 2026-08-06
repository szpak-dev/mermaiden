from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import Violation
from ....core.diagram import Diagram
from ..elements.elements import Start
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="exactly_one_start")
@dataclass(frozen=True, slots=True)
class ExactlyOneStart(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.one_start"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        count = sum(isinstance(item, Start) for item in diagram.elements)
        if count == 1:
            return ()
        return (self.violation(f"Flowchart requires exactly one start; found {count}."),)
