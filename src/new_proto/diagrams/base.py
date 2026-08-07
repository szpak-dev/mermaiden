from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar, Protocol

from ..core.annotation import Annotation
from ..core.constraint import ChangeReport, Constraint, ValidationReport
from ..core.diagram import Diagram
from ..core.element import Element
from ..core.error import OperationError
from ..core.relation import Relation
from ..runtime.diagrams.aggregate import DiagramAggregate
from ..runtime.diagrams.observer import ConstraintInspection


class DiagramObserver[ConstraintT: Constraint](ConstraintInspection):
    structure: ConstraintInspection
    constraints: Sequence[ConstraintT]

    def inspect(self, diagram: Diagram) -> ValidationReport:
        structural = self.structure.inspect(diagram)
        domain = tuple(violation for constraint in self.constraints for violation in diagram.accept(constraint))
        return ValidationReport((*structural.violations, *domain))


class AnnotationFactory(Protocol):
    def create(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str],
        relation_ids: Sequence[str],
    ) -> Annotation: ...


@dataclass(frozen=True, slots=True)
class DiagramDefinition:
    kind: str
    entity_name: str
    container_name: str
    relation_name: str
    annotation_name: str
    entity: Callable[[str, str], Element]
    container: Callable[[str, str], Element]
    relation: Callable[[str, tuple[str, ...], str], Relation]
    annotation: AnnotationFactory


class DefinedDiagram(DiagramAggregate):
    definition: ClassVar[DiagramDefinition]

    @property
    def kind(self) -> str:
        return self.definition.kind

    def add_container(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(
            f"add {self.definition.container_name} '{id}'",
            self.definition.container(id, label),
            parent_id,
        )

    def add_entity(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(
            f"add {self.definition.entity_name} '{id}'",
            self.definition.entity(id, label),
            parent_id,
        )

    def connect(self, id: str, element_ids: Sequence[str], label: str = "") -> ChangeReport:
        return self._add_relation(
            f"add {self.definition.relation_name} '{id}'",
            self.definition.relation(id, tuple(element_ids), label),
        )

    def annotate(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str] = (),
        relation_ids: Sequence[str] = (),
    ) -> ChangeReport:
        operation = f"add {self.definition.annotation_name} '{id}'"
        try:
            annotation = self.definition.annotation.create(id, data, element_ids, relation_ids)
        except OperationError as error:
            self._reject(operation, str(error))
        return self._add_annotation(operation, annotation)
