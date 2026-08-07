from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from wireup import injectable

from ...core.annotation import Annotation, DataAnnotation, TargetKind, TargetRef
from ...core.constraint import ChangeReport, ValidationReport
from ...core.diagram import Diagram
from ...core.element import Container, Element, Entity
from ...core.error import OperationError
from ...core.relation import Relation
from .annotations import Annotations
from .changes import Changes
from .elements import Elements
from .observer import ConstraintInspection
from .relations import Relations
from .state import DiagramState


@injectable(as_type=Diagram, lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramAggregate(Diagram):
    state: DiagramState
    elements: Elements
    relations: Relations
    annotations: Annotations
    changes: Changes
    observer: ConstraintInspection

    @property
    def kind(self) -> str:
        return "diagram"

    @property
    def root_elements(self) -> tuple[Element, ...]:
        return self.state.current.elements

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

    def add_container(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add container '{id}'", Container(id, label), parent_id)

    def add_entity(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add entity '{id}'", Entity(id, label), parent_id)

    def connect(
        self,
        id: str,
        element_ids: Sequence[str],
        label: str = "",
    ) -> ChangeReport:
        return self._add_relation(f"connect relation '{id}'", Relation(id, tuple(element_ids), label))

    def annotate(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str] = (),
        relation_ids: Sequence[str] = (),
    ) -> ChangeReport:
        targets = (
            *(TargetRef(TargetKind.ELEMENT, item) for item in element_ids),
            *(TargetRef(TargetKind.RELATION, item) for item in relation_ids),
        )
        return self._add_annotation(f"add annotation '{id}'", DataAnnotation(id, targets, dict(data)))

    def remove_element(self, id: str, *, cascade: bool = False) -> ChangeReport:
        operation = f"remove element '{id}'"
        try:
            candidate, removed_ids = self.elements.remove(id)
            dependent_relations = tuple(
                item.id
                for item in self.state.current.relations
                if set(item.element_ids).intersection(removed_ids)
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
            self.changes.reject(operation, str(error))
        return self.changes.apply(operation, candidate, self)

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
            self.changes.reject(operation, str(error))
        return self.changes.apply(operation, candidate, self)

    def remove_annotation(self, id: str) -> ChangeReport:
        operation = f"remove annotation '{id}'"
        try:
            candidate = self.annotations.remove(id)
        except OperationError as error:
            self.changes.reject(operation, str(error))
        return self.changes.apply(operation, candidate, self)

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
