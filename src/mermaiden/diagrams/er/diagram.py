from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import EntityRelationshipDiagramConfiguration
from .constraints.constraint import EntityRelationshipDiagramConstraint
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
    syntax: ClassVar[str] = "erDiagram"
    name: ClassVar[str] = "Entity relationship diagram"
    config_key: ClassVar[str] = "er"
    schema_definition: ClassVar[str] = "ErDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}

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
