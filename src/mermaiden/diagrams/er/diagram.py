from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.domain import ChangeReport, Container, Element
from ..domain import DiagramDefinition, DiagramModel
from .configuration import EntityRelationshipDiagramConfiguration
from .constraints import EntityRelationshipDiagramConstraint
from .elements import Entity, EntityAttribute
from .relations import EntityRelationship


@injectable(as_type=DiagramModel, qualifier="er", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class EntityRelationshipDiagram(DiagramModel):
    constraints: Sequence[EntityRelationshipDiagramConstraint]
    configuration: EntityRelationshipDiagramConfiguration = field(
        default_factory=EntityRelationshipDiagramConfiguration,
        init=False,
    )
    direction: str = field(default="TB", init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "erDiagram",
        "Entity relationship diagram",
        "er",
        "ErDiagramConfig",
    )

    def accepts_parent(self, element_type: type[Element], parent_type: type[Container] | None) -> bool:
        if element_type is Entity:
            return parent_type is None
        return element_type is EntityAttribute and parent_type is Entity

    def set_direction(self, direction: str) -> None:
        object.__setattr__(self, "direction", direction)

    def add_entity(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add entity '{id}'", Entity(id=id, label=label))

    def add_attribute(
        self,
        id: str,
        label: str,
        data_type: str,
        entity_id: str,
        keys: tuple[str, ...] = (),
        comment: str = "",
    ) -> ChangeReport:
        return self._add_element(
            f"add attribute '{id}'",
            EntityAttribute(id=id, label=label, data_type=data_type, keys=keys, comment=comment),
            entity_id,
        )

    def add_relationship(
        self,
        id: str,
        source_id: str,
        target_id: str,
        label: str,
        notation: str = "||--||",
    ) -> ChangeReport:
        return self._add_relation(
            f"add relationship '{id}",
            EntityRelationship(id=id, element_ids=(source_id, target_id), label=label, notation=notation),
        )
