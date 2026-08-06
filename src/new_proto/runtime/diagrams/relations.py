from dataclasses import dataclass, replace

from wireup import injectable

from ...core.error import OperationError
from ...core.relation import Relation
from .state import DiagramData, DiagramState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Relations:
    state: DiagramState

    def add(self, relation: Relation) -> DiagramData:
        return replace(
            self.state.current,
            relations=(*self.state.current.relations, relation),
        )

    def connect(self, id: str, element_ids: tuple[str, ...], label: str = "") -> DiagramData:
        return self.add(Relation(id, element_ids, label))

    def remove(self, id: str) -> DiagramData:
        if not any(item.id == id for item in self.state.current.relations):
            raise OperationError(f"Relation '{id}' does not exist.")
        return replace(
            self.state.current,
            relations=tuple(item for item in self.state.current.relations if item.id != id),
        )

    def without_elements(self, data: DiagramData, element_ids: tuple[str, ...]) -> DiagramData:
        removed = set(element_ids)
        relations = tuple(
            item for item in data.relations if not removed.intersection(item.element_ids)
        )
        return replace(data, relations=relations)

    def find(self, element_id: str = "") -> tuple[Relation, ...]:
        if not element_id:
            return self.state.current.relations
        return tuple(
            item for item in self.state.current.relations if element_id in item.element_ids
        )
