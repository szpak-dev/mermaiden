from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramModel
from .configuration import C4ContextDiagramConfiguration
from .constraints import C4ContextDiagramConstraint
from .elements import Person, System, SystemDb, SystemQueue
from .relations import Relationship, RelationshipDirection


@injectable(as_type=DiagramModel, qualifier="c4", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class C4ContextDiagram(DiagramModel):
    constraints: Sequence[C4ContextDiagramConstraint]
    configuration: C4ContextDiagramConfiguration = field(default_factory=C4ContextDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "C4Context",
        "C4 Context diagram",
        "c4",
        "C4DiagramConfig",
    )

    def add_person(self, id: str, label: str, description: str = "") -> ChangeReport:
        return self._add_element(f"add person '{id}'", Person(id=id, label=label, description=description))

    def add_system(self, id: str, label: str, description: str = "", technology: str = "") -> ChangeReport:
        return self._add_element(
            f"add system '{id}'", System(id=id, label=label, description=description, technology=technology)
        )

    def add_database(self, id: str, label: str, description: str = "", technology: str = "") -> ChangeReport:
        return self._add_element(
            f"add database '{id}'", SystemDb(id=id, label=label, description=description, technology=technology)
        )

    def add_queue(self, id: str, label: str, description: str = "", technology: str = "") -> ChangeReport:
        return self._add_element(
            f"add queue '{id}'", SystemQueue(id=id, label=label, description=description, technology=technology)
        )

    def add_relationship(
        self,
        id: str,
        source_id: str,
        target_id: str,
        label: str,
        direction: RelationshipDirection = RelationshipDirection.DEFAULT,
    ) -> ChangeReport:
        return self._add_relation(
            f"add relationship '{id}'",
            Relationship(id=id, element_ids=(source_id, target_id), label=label, direction=direction),
        )

    def set_relationship_label_offset(self, id: str, offset_x: int, offset_y: int) -> ChangeReport:
        operation = f"set relationship label offset '{id}'"
        relationship = next(
            (item for item in self.find_relations() if isinstance(item, Relationship) and item.id == id),
            None,
        )
        if relationship is None:
            self._reject(operation, f"Relationship '{id}' does not exist.")
        values = relationship.model_dump()
        values.update(offset_x=offset_x, offset_y=offset_y)
        updated = Relationship.model_validate(values)
        candidate = replace(
            self.state.current,
            relations=tuple(updated if item is relationship else item for item in self.state.current.relations),
        )
        return self._apply(operation, candidate)
