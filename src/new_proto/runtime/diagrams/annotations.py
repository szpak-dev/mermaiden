from dataclasses import dataclass, replace

from ...core.annotation import Annotation, TargetKind
from ...core.error import OperationError
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
            item
            for item in self.state.current.annotations
            if any(target.id == target_id for target in item.targets)
        )
