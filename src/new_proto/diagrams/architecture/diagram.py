from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..base import DefinedDiagram, DiagramDefinition
from .annotations import ArchitectureNotes
from .changes import ArchitectureChanges
from .elements import ArchitectureGroup, Junction, Service
from .observer import ArchitectureObserver
from .relations import Edge, Port
from .runtime import ArchitectureAnnotations, ArchitectureElements, ArchitectureRelations, ArchitectureState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Architecture(DefinedDiagram):
    state: ArchitectureState
    elements: ArchitectureElements
    relations: ArchitectureRelations
    annotations: ArchitectureAnnotations
    changes: ArchitectureChanges
    observer: ArchitectureObserver
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "architecture-beta", "service", "group", "edge", "note", Service, ArchitectureGroup, Edge, ArchitectureNotes()
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
        return self.annotate(id, {"text": text}, (element_id,))
