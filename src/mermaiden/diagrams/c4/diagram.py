from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import C4ContextDiagramConfiguration
from .constraints.constraint import C4ContextDiagramConstraint
from .elements import Person, System, SystemDb, SystemQueue
from .relations import Relationship


@injectable(as_type=DiagramModel, qualifier="c4", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class C4ContextDiagram(DiagramModel):
    constraints: Sequence[C4ContextDiagramConstraint]
    configuration: C4ContextDiagramConfiguration = field(default_factory=C4ContextDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "C4Context"
    name: ClassVar[str] = "C4 Context diagram"
    config_key: ClassVar[str] = "c4"
    schema_definition: ClassVar[str] = "C4DiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

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
