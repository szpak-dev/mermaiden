from dataclasses import dataclass
from typing import Never

from wireup import injectable

from ...core.constraint import ChangeReport
from ...core.diagram import Diagram
from ...runtime.diagrams.changes import Changes
from ...runtime.diagrams.state import DiagramData
from ...runtime.diagrams.transaction import ChangeTransaction
from .observer import FlowchartObserver


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class FlowchartChanges(Changes):
    transaction: ChangeTransaction
    observer: FlowchartObserver

    def apply(self, operation: str, candidate: DiagramData, diagram: Diagram) -> ChangeReport:
        return self.transaction.apply(operation, candidate, diagram, self.observer)

    def reject(self, operation: str, message: str) -> Never:
        return self.transaction.reject(operation, message)
