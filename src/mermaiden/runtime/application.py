from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ..core.domain import (
    Constraint,
    Diagram,
    ValidationReport,
)
from .domain import ConstraintInspection


@injectable(as_type=ConstraintInspection)
@dataclass(frozen=True, slots=True)
class ConstraintObserver(ConstraintInspection):
    constraints: Sequence[Constraint]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        return ValidationReport(
            tuple(violation for constraint in self.constraints for violation in diagram.accept(constraint))
        )
