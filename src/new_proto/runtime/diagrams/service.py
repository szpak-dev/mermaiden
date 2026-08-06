from dataclasses import dataclass, replace

from wireup import injectable

from ...core.annotation import Annotation, TargetKind
from ...core.constraint import Constraint, ValidationReport
from ...core.element import Element
from ...core.relation import Relation
from .diagram import FrozenDiagram
from .draft import DiagramDraft
from .errors import DiagramBuildError, DiagramValidationError, DuplicateIdError
from .validator import DiagramValidator


@injectable
@dataclass(frozen=True, slots=True)
class DiagramService:
    validator: DiagramValidator

    def start(self, diagram_id: str, constraints: tuple[Constraint, ...] = ()) -> DiagramDraft:
        if not diagram_id.strip():
            raise DiagramBuildError("Diagram ID must not be blank.")
        return DiagramDraft(diagram_id, constraints=constraints)

    def add_element(self, draft: DiagramDraft, element: Element) -> DiagramDraft:
        self._ensure_unique(draft.elements, element.id, "element")
        return replace(draft, elements=(*draft.elements, element))

    def add_relation(self, draft: DiagramDraft, relation: Relation) -> DiagramDraft:
        self._ensure_unique(draft.relations, relation.id, "relation")
        return replace(draft, relations=(*draft.relations, relation))

    def add_annotation(self, draft: DiagramDraft, annotation: Annotation) -> DiagramDraft:
        self._ensure_unique(draft.annotations, annotation.id, "annotation")
        return replace(draft, annotations=(*draft.annotations, annotation))

    def remove_element(self, draft: DiagramDraft, element_id: str, *, cascade: bool = False) -> DiagramDraft:
        if not any(item.id == element_id for item in draft.elements):
            raise DiagramBuildError(f"Unknown element '{element_id}'.")
        removed = {element_id}
        while children := {
            item.id for item in draft.elements if item.owner_id in removed and item.id not in removed
        }:
            removed.update(children)
        relations = {item.id for item in draft.relations if set(item.participant_ids) & removed}
        annotations = {
            item.id
            for item in draft.annotations
            if any(
                (target.kind is TargetKind.ELEMENT and target.id in removed)
                or (target.kind is TargetKind.RELATION and target.id in relations)
                for target in item.targets
            )
        }
        if not cascade and (len(removed) > 1 or relations or annotations):
            raise DiagramBuildError(f"Element '{element_id}' still has dependants; use cascade=True.")
        return replace(
            draft,
            elements=tuple(item for item in draft.elements if item.id not in removed),
            relations=tuple(item for item in draft.relations if item.id not in relations),
            annotations=tuple(item for item in draft.annotations if item.id not in annotations),
        )

    def inspect(self, draft: DiagramDraft) -> ValidationReport:
        return self.validator.inspect(self.build(draft, validate=False))

    def build(self, draft: DiagramDraft, *, validate: bool = True) -> FrozenDiagram:
        diagram = FrozenDiagram(
            draft.id,
            draft.elements,
            draft.relations,
            draft.annotations,
            draft.constraints,
        )
        if validate:
            report = self.validator.inspect(diagram)
            if not report:
                raise DiagramValidationError(report)
        return diagram

    @staticmethod
    def _ensure_unique(items: tuple[object, ...], identity: str, kind: str) -> None:
        if not identity.strip():
            raise DiagramBuildError(f"{kind.title()} ID must not be blank.")
        if any(getattr(item, "id", None) == identity for item in items):
            raise DuplicateIdError(f"Duplicate {kind} ID '{identity}'.")
