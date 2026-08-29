from collections.abc import Mapping
from dataclasses import dataclass, replace

from pydantic import ValidationError

from ...core.error import OperationError
from ...core.relation import Relation
from .state import DiagramData, DiagramState


@dataclass(frozen=True, slots=True)
class Relations:
    state: DiagramState

    def add(self, relation: Relation) -> DiagramData:
        return replace(
            self.state.current,
            relations=(*self.state.current.relations, relation),
        )

    def remove(self, id: str) -> DiagramData:
        if not any(item.id == id for item in self.state.current.relations):
            raise OperationError(f"Relation '{id}' does not exist.")
        return replace(
            self.state.current,
            relations=tuple(item for item in self.state.current.relations if item.id != id),
        )

    def update(self, id: str, kind: str, changes: Mapping[str, object]) -> DiagramData:
        matches = tuple(item for item in self.state.current.relations if item.id == id)
        if not matches:
            raise OperationError(f"Relation '{id}' does not exist.")
        if len(matches) > 1:
            raise OperationError(f"Relation '{id}' is duplicated.")
        target = next(iter(matches))
        if target.kind != kind:
            raise OperationError(f"Relation '{id}' has kind '{target.kind}', not '{kind}'.")
        if not changes:
            raise OperationError("Relation changes must contain at least one field.")
        if "id" in changes:
            raise OperationError("Relation field cannot be updated: id.")
        unknown = set(changes).difference(type(target).model_fields)
        if unknown:
            raise OperationError(f"Unknown relation fields: {', '.join(sorted(unknown))}.")
        values = target.model_dump()
        values.update(changes)
        try:
            updated = type(target).model_validate(values)
        except ValidationError as error:
            raise OperationError(f"Relation '{id}' changes are invalid: {error}") from error
        return replace(
            self.state.current,
            relations=tuple(updated if item is target else item for item in self.state.current.relations),
        )

    def without_elements(self, data: DiagramData, element_ids: tuple[str, ...]) -> DiagramData:
        removed = set(element_ids)
        relations = tuple(item for item in data.relations if not removed.intersection(item.element_ids))
        return replace(data, relations=relations)

    def find(self, element_id: str = "") -> tuple[Relation, ...]:
        if not element_id:
            return self.state.current.relations
        return tuple(item for item in self.state.current.relations if element_id in item.element_ids)
