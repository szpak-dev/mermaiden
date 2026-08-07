from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .annotations import ArchitectureNotes
from .constraints import ArchitectureConstraint
from .elements import ArchitectureGroup, Junction, Service
from .relations import Edge, Port


@injectable(as_type=DiagramModel, qualifier="architecture", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Architecture(DiagramModel):
    constraints: Sequence[ArchitectureConstraint]
    syntax: ClassVar[str] = "architecture-beta"
    name: ClassVar[str] = "Architecture diagram"
    config_key: ClassVar[str] = "architecture"
    schema_definition: ClassVar[str] = "ArchitectureDiagramConfig"

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
