from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ValidationReport
from ...core.diagram import Diagram


@injectable
@dataclass(frozen=True, slots=True)
class ConstraintObserver:
    constraints: Sequence[Constraint]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        return ValidationReport(
            tuple(
                violation
                for constraint in self.constraints
                for violation in diagram.accept(constraint)
            )
        )
