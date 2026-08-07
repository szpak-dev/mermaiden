from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import EntityRelationshipDiagramConfiguration
from .constraints import EntityRelationshipAnnotationMember, EntityRelationshipDiagramConstraint
from .elements import Entity, EntityAttribute, EntityRelationshipElementMember
from .relations import EntityRelationship, EntityRelationshipRelationMember


@injectable(as_type=DiagramModel, qualifier="er", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class EntityRelationshipDiagram(DiagramModel):
    constraints: Sequence[EntityRelationshipDiagramConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "er.member_type",
        EntityRelationshipElementMember,
        EntityRelationshipRelationMember,
        EntityRelationshipAnnotationMember,
    )
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


    def set_direction(self, direction: str) -> None:
        object.__setattr__(self, "direction", direction)

    def add_entity(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add entity '{id}'", Entity(id, label))

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
            EntityAttribute(id, label, data_type, keys, comment),
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
            EntityRelationship(id, (source_id, target_id), label, notation),
        )
