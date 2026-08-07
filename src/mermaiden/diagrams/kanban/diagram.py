from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import KanbanDiagramConfiguration
from .constraints.constraint import KanbanDiagramConstraint
from .elements import Column, Task


@injectable(as_type=DiagramModel, qualifier="kanban", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class KanbanDiagram(DiagramModel):
    constraints: Sequence[KanbanDiagramConstraint]
    configuration: KanbanDiagramConfiguration = field(default_factory=KanbanDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "kanban"
    name: ClassVar[str] = "Kanban diagram"
    config_key: ClassVar[str] = "kanban"
    schema_definition: ClassVar[str] = "KanbanDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def add_column(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add column '{id}'", Column(id, label))

    def add_task(
        self,
        id: str,
        label: str,
        column_id: str,
        assigned: str = "",
        ticket: str = "",
        priority: str = "",
    ) -> ChangeReport:
        return self._add_element(
            f"add task '{id}'",
            Task(id, label, assigned, ticket, priority),
            column_id,
        )
