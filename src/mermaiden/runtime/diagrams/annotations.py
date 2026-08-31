from collections.abc import Mapping
from dataclasses import dataclass, replace

from pydantic import ValidationError

from ...core.domain import Annotation, OperationError, TargetKind
from .state import DiagramData, DiagramState


@dataclass(frozen=True, slots=True)
class Annotations:
    state: DiagramState

    def add_annotation(self, annotation: Annotation) -> DiagramData:
        return replace(
            self.state.current,
            annotations=(*self.state.current.annotations, annotation),
        )

    def remove(self, id: str) -> DiagramData:
        if not any(item.id == id for item in self.state.current.annotations):
            raise OperationError(f"Annotation '{id}' does not exist.")
        return replace(
            self.state.current,
            annotations=tuple(item for item in self.state.current.annotations if item.id != id),
        )

    def update(self, id: str, kind: str, changes: Mapping[str, object]) -> DiagramData:
        matches = tuple(item for item in self.state.current.annotations if item.id == id)
        if not matches:
            raise OperationError(f"Annotation '{id}' does not exist.")
        if len(matches) > 1:
            raise OperationError(f"Annotation '{id}' is duplicated.")
        target = next(iter(matches))
        if target.kind != kind:
            raise OperationError(f"Annotation '{id}' has kind '{target.kind}', not '{kind}'.")
        if not changes:
            raise OperationError("Annotation changes must contain at least one field.")
        if "id" in changes:
            raise OperationError("Annotation field cannot be updated: id.")
        unknown = set(changes).difference(type(target).model_fields)
        if unknown:
            raise OperationError(f"Unknown annotation fields: {', '.join(sorted(unknown))}.")
        values = target.model_dump()
        values.update(changes)
        try:
            updated = type(target).model_validate(values)
        except ValidationError as error:
            raise OperationError(f"Annotation '{id}' changes are invalid: {error}") from error
        return replace(
            self.state.current,
            annotations=tuple(updated if item is target else item for item in self.state.current.annotations),
        )

    def without_targets(
        self,
        data: DiagramData,
        element_ids: tuple[str, ...] = (),
        relation_ids: tuple[str, ...] = (),
    ) -> DiagramData:
        removed_elements = set(element_ids)
        removed_relations = set(relation_ids)
        annotations = tuple(
            item
            for item in data.annotations
            if not any(
                (target.kind is TargetKind.ELEMENT and target.id in removed_elements)
                or (target.kind is TargetKind.RELATION and target.id in removed_relations)
                for target in item.targets
            )
        )
        return replace(data, annotations=annotations)

    def find(self, target_id: str = "") -> tuple[Annotation, ...]:
        if not target_id:
            return self.state.current.annotations
        return tuple(
            item for item in self.state.current.annotations if any(target.id == target_id for target in item.targets)
        )
