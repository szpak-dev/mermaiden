from dataclasses import dataclass
from typing import Never

from wireup import injectable

from ...core.constraint import (
    ChangeRejected,
    ChangeReport,
    ConstraintLevel,
    ValidationReport,
    Violation,
)
from ...core.diagram import Diagram
from .observer import ConstraintObserver
from .state import DiagramData, DiagramState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramChanges:
    state: DiagramState
    observer: ConstraintObserver

    def apply(self, operation: str, candidate: DiagramData, diagram: Diagram) -> ChangeReport:
        before = self.observer.inspect(diagram)
        self.state.stage(candidate)
        try:
            after = self.observer.inspect(diagram)
        except Exception:
            self.state.rollback()
            raise
        report = ChangeReport(operation, before, after, after.can_commit)
        if not report.accepted:
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
