from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ValidationReport
from ...core.diagram import Diagram


class ConstraintInspection(ABC):
    @abstractmethod
    def inspect(self, diagram: Diagram) -> ValidationReport: ...


@injectable(as_type=ConstraintInspection)
@dataclass(frozen=True, slots=True)
class ConstraintObserver(ConstraintInspection):
    constraints: Sequence[Constraint]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        return ValidationReport(
            tuple(
                violation
                for constraint in self.constraints
                for violation in diagram.accept(constraint)
            )
        )
