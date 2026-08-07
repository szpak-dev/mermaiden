from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .annotations import ArchitectureAnnotationMember, ArchitectureNotes
from .configuration import ArchitectureDiagramConfiguration
from .constraints import ArchitectureConstraint
from .elements import ArchitectureElementMember, ArchitectureGroup, Junction, Service
from .relations import ArchitectureRelationMember, Edge, Port


@injectable(as_type=DiagramModel, qualifier="architecture", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Architecture(DiagramModel):
    constraints: Sequence[ArchitectureConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "architecture.members",
        ArchitectureElementMember,
        ArchitectureRelationMember,
        ArchitectureAnnotationMember,
    )
    configuration: ArchitectureDiagramConfiguration = field(
        default_factory=ArchitectureDiagramConfiguration,
        init=False,
    )
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "architecture-beta",
        "Architecture diagram",
        "architecture",
        "ArchitectureDiagramConfig",
    )


    def add_group(self, id: str, label: str, parent_id: str = "", columns: int = 1) -> ChangeReport:
        return self._add_element(f"add group '{id}'", ArchitectureGroup(id, label, (), columns), parent_id)

    def add_service(self, id: str, label: str, group_id: str = "") -> ChangeReport:
        return self._add_element(f"add service '{id}'", Service(id, label), group_id)

    def add_junction(self, id: str, label: str = "", group_id: str = "") -> ChangeReport:
        return self._add_element(f"add junction '{id}'", Junction(id, label or id), group_id)

    def add_edge(
        self,
        id: str,
        source_id: str,
        target_id: str,
        source_port: Port = Port.RIGHT,
        target_port: Port = Port.LEFT,
        label: str = "",
    ) -> ChangeReport:
        return self._add_relation(f"add edge '{id}'", Edge(id, (source_id, target_id), label, source_port, target_port))

    def add_note(self, id: str, element_id: str, text: str) -> ChangeReport:
        return self._annotate(f"add note '{id}'", ArchitectureNotes(), id, {"text": text}, (element_id,))
