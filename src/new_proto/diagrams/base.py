from collections.abc import Sequence
from typing import Never

from ..core.annotation import Annotation
from ..core.constraint import ChangeReport, Constraint, ValidationReport
from ..core.diagram import Diagram
from ..core.element import Element
from ..core.error import OperationError
from ..core.relation import Relation
from ..runtime.diagrams.aggregate import DiagramAggregate
from ..runtime.diagrams.changes import Changes
from ..runtime.diagrams.observer import ConstraintInspection
from ..runtime.diagrams.state import DiagramData
from ..runtime.diagrams.transaction import ChangeTransaction


class DiagramChanges[TransactionT: ChangeTransaction, ObserverT: ConstraintInspection](Changes):
    transaction: TransactionT
    observer: ObserverT

    def apply(self, operation: str, candidate: DiagramData, diagram: Diagram) -> ChangeReport:
        return self.transaction.apply(operation, candidate, diagram, self.observer)

    def reject(self, operation: str, message: str) -> Never:
        return self.transaction.reject(operation, message)


class DiagramObserver[ConstraintT: Constraint](ConstraintInspection):
    structure: ConstraintInspection
    constraints: Sequence[ConstraintT]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        structural = self.structure.inspect(diagram)
        domain = tuple(violation for constraint in self.constraints for violation in diagram.accept(constraint))
        return ValidationReport((*structural.violations, *domain))


class DomainDiagram(DiagramAggregate):
    def _add_element(self, operation: str, element: Element, parent_id: str = "") -> ChangeReport:
        try:
            candidate = self.elements.add(element, parent_id)
        except OperationError as error:
            self.changes.reject(operation, str(error))
        return self.changes.apply(operation, candidate, self)

    def _add_relation(self, operation: str, relation: Relation) -> ChangeReport:
        return self.changes.apply(operation, self.relations.add(relation), self)

    def _add_annotation(self, operation: str, annotation: Annotation) -> ChangeReport:
        return self.changes.apply(operation, self.annotations.add_annotation(annotation), self)
