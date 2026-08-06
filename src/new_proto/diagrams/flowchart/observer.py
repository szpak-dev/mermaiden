from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import ValidationReport
from ...core.diagram import Diagram
from ...runtime.diagrams.observer import ConstraintInspection
from .constraints.constraint import FlowchartConstraint


@injectable
@dataclass(frozen=True, slots=True)
class FlowchartObserver(ConstraintInspection):
    structure: ConstraintInspection
    constraints: Sequence[FlowchartConstraint]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        structural = self.structure.inspect(diagram)
        domain = tuple(
            violation
            for constraint in self.constraints
            for violation in diagram.accept(constraint)
        )
        return ValidationReport((*structural.violations, *domain))
