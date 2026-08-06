from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ValidationReport
from ...core.diagram import Diagram


@injectable
@dataclass(frozen=True, slots=True)
class DiagramValidator:
    constraints: Sequence[Constraint]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        domain = tuple(item for item in diagram.constraints if isinstance(item, Constraint))
        violations = tuple(
            issue
            for constraint in (*self.constraints, *domain)
            for issue in diagram.accept(constraint)
        )
        return ValidationReport(violations)
