from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import C4ContextDiagramConfiguration
from .constraints import C4AnnotationMember, C4ContextDiagramConstraint
from .elements import C4ElementMember, Person, System, SystemDb, SystemQueue
from .relations import C4RelationMember, Relationship


@injectable(as_type=DiagramModel, qualifier="c4", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class C4ContextDiagram(DiagramModel):
    constraints: Sequence[C4ContextDiagramConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "c4.member_type",
        C4ElementMember,
        C4RelationMember,
        C4AnnotationMember,
    )
    configuration: C4ContextDiagramConfiguration = field(default_factory=C4ContextDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "C4Context",
        "C4 Context diagram",
        "c4",
        "C4DiagramConfig",
    )


    def add_person(self, id: str, label: str, description: str = "") -> ChangeReport:
        return self._add_element(f"add person '{id}'", Person(id, label, description))

    def add_system(self, id: str, label: str, description: str = "", technology: str = "") -> ChangeReport:
        return self._add_element(f"add system '{id}'", System(id, label, description, technology))

    def add_database(self, id: str, label: str, description: str = "", technology: str = "") -> ChangeReport:
        return self._add_element(f"add database '{id}'", SystemDb(id, label, description, technology))

    def add_queue(self, id: str, label: str, description: str = "", technology: str = "") -> ChangeReport:
        return self._add_element(f"add queue '{id}'", SystemQueue(id, label, description, technology))

    def add_relationship(self, id: str, source_id: str, target_id: str, label: str) -> ChangeReport:
        return self._add_relation(f"add relationship '{id}'", Relationship(id, (source_id, target_id), label))
