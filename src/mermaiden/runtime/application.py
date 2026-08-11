from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Never

from wireup import injectable

from ..core.constraint import ChangeRejected, ChangeReport, Constraint, ConstraintLevel, ValidationReport, Violation
from ..core.diagram import Diagram
from .diagrams.annotations import Annotations
from .diagrams.elements import Elements
from .diagrams.relations import Relations
from .diagrams.state import DiagramData, DiagramState
from .domain import ConstraintInspection


@dataclass(frozen=True, slots=True)
class ChangeTransaction:
    state: DiagramState

    def apply(
        self,
        operation: str,
        candidate: DiagramData,
        diagram: Diagram,
        observer: ConstraintInspection,
    ) -> ChangeReport:
        before = observer.inspect(diagram)
        self.state.stage(candidate)
        try:
            after = observer.inspect(diagram)
        except Exception:
            self.state.rollback()
            raise
        report = ChangeReport(operation, before, after, after.can_commit)
        if not report.accepted and before.can_commit:
            self.state.rollback()
            raise ChangeRejected(operation, after)
        self.state.commit()
        return report

    def reject(self, operation: str, message: str) -> Never:
        current = ValidationReport(
            (
                Violation(
                    code="operation.rejected",
                    message=message,
                    path=operation,
                    level=ConstraintLevel.BLOCKING,
                ),
            )
        )
        raise ChangeRejected(operation, current)


@dataclass(frozen=True, slots=True)
class DiagramRuntime:
    state: DiagramState = field(default_factory=DiagramState)
    elements: Elements = field(init=False)
    relations: Relations = field(init=False)
    annotations: Annotations = field(init=False)
    transaction: ChangeTransaction = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "elements", Elements(self.state))
        object.__setattr__(self, "relations", Relations(self.state))
        object.__setattr__(self, "annotations", Annotations(self.state))
        object.__setattr__(self, "transaction", ChangeTransaction(self.state))


@injectable(as_type=ConstraintInspection)
@dataclass(frozen=True, slots=True)
class ConstraintObserver(ConstraintInspection):
    constraints: Sequence[Constraint]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        return ValidationReport(
            tuple(violation for constraint in self.constraints for violation in diagram.accept(constraint))
        )
