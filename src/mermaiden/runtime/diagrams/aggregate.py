from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Never, Protocol

from wireup import injectable

from ...core.annotation import Annotation, TargetKind
from ...core.constraint import ChangeReport, ValidationReport
from ...core.diagram import Diagram
from ...core.element import Element
from ...core.error import OperationError
from ...core.relation import Relation
from ..application import DiagramRuntime
from ..domain import ConstraintInspection
from .state import DiagramData


class AnnotationFactory(Protocol):
    def create(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str],
        relation_ids: Sequence[str],
    ) -> Annotation: ...


@injectable(as_type=Diagram, lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramAggregate(Diagram):
    runtime: DiagramRuntime = field(default_factory=DiagramRuntime, init=False)

    @property
    def observer(self) -> ConstraintInspection:
        raise NotImplementedError

    @property
    def state(self):
        return self.runtime.state

    @property
    def elements(self):
        return self.runtime.elements

    @property
    def relations(self):
        return self.runtime.relations

    @property
    def annotations(self):
        return self.runtime.annotations

    @property
    def kind(self) -> str:
        return "diagram"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {}

    @property
    def root_elements(self) -> tuple[Element, ...]:
        return self.state.current.elements

    def _add_element(self, operation: str, element: Element, parent_id: str = "") -> ChangeReport:
        try:
            candidate = self.elements.add(element, parent_id)
        except OperationError as error:
            self._reject(operation, str(error))
        return self._apply(operation, candidate)

    def _add_relation(self, operation: str, relation: Relation) -> ChangeReport:
        return self._apply(operation, self.relations.add(relation))

    def _add_annotation(self, operation: str, annotation: Annotation) -> ChangeReport:
        return self._apply(operation, self.annotations.add_annotation(annotation))

    def _annotate(
        self,
        operation: str,
        factory: AnnotationFactory,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str] = (),
        relation_ids: Sequence[str] = (),
    ) -> ChangeReport:
        try:
            annotation = factory.create(id, data, element_ids, relation_ids)
        except OperationError as error:
            self._reject(operation, str(error))
        return self._add_annotation(operation, annotation)

    def remove_element(self, id: str, *, cascade: bool = False) -> ChangeReport:
        operation = f"remove element '{id}'"
        try:
            candidate, removed_ids = self.elements.remove(id)
            dependent_relations = tuple(
                item.id for item in self.state.current.relations if set(item.element_ids).intersection(removed_ids)
            )
            dependent_annotations = tuple(
                item.id
                for item in self.state.current.annotations
                if any(
                    (target.kind is TargetKind.ELEMENT and target.id in removed_ids)
                    or (target.kind is TargetKind.RELATION and target.id in dependent_relations)
                    for target in item.targets
                )
            )
            if not cascade and (len(removed_ids) > 1 or dependent_relations or dependent_annotations):
                raise OperationError(f"Element '{id}' still has dependants; use cascade=True.")
            candidate = self.relations.without_elements(candidate, removed_ids)
            candidate = self.annotations.without_targets(
                candidate,
                removed_ids,
                dependent_relations,
            )
        except OperationError as error:
            self._reject(operation, str(error))
        return self._apply(operation, candidate)

    def remove_relation(self, id: str) -> ChangeReport:
        operation = f"remove relation '{id}'"
        try:
            if any(
                target.id == id and target.kind is TargetKind.RELATION
                for annotation in self.state.current.annotations
                for target in annotation.targets
            ):
                raise OperationError(f"Relation '{id}' still has annotations; remove them first.")
            candidate = self.relations.remove(id)
        except OperationError as error:
            self._reject(operation, str(error))
        return self._apply(operation, candidate)

    def remove_annotation(self, id: str) -> ChangeReport:
        operation = f"remove annotation '{id}'"
        try:
            candidate = self.annotations.remove(id)
        except OperationError as error:
            self._reject(operation, str(error))
        return self._apply(operation, candidate)

    def find_element(self, id: str) -> Element | None:
        return self.elements.find(id)

    def walk_elements(self, parent_id: str = "") -> Sequence[Element]:
        return self.elements.walk(parent_id)

    def find_relations(self, element_id: str = "") -> Sequence[Relation]:
        return self.relations.find(element_id)

    def find_annotations(self, target_id: str = "") -> Sequence[Annotation]:
        return self.annotations.find(target_id)

    def validate(self) -> ValidationReport:
        return self.observer.inspect(self)

    def _apply(self, operation: str, candidate: DiagramData) -> ChangeReport:
        return self.runtime.transaction.apply(operation, candidate, self, self.observer)

    def _reject(self, operation: str, message: str) -> Never:
        self.runtime.transaction.reject(operation, message)
