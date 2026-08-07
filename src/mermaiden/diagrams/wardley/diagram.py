from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import WardleyDiagramConfiguration
from .constraints.constraint import WardleyDiagramConstraint
from .elements import Component, Evolution
from .relations import Dependency


@injectable(as_type=DiagramModel, qualifier="wardley", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class WardleyDiagram(DiagramModel):
    constraints: Sequence[WardleyDiagramConstraint]
    configuration: WardleyDiagramConfiguration = field(default_factory=WardleyDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "wardley-beta"
    name: ClassVar[str] = "Wardley map"
    config_key: ClassVar[str] = "wardley-beta"
    schema_definition: ClassVar[str] = "WardleyDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def add_component(
        self, id: str, label: str, visibility: float, evolution: float, decorator: str = ""
    ) -> ChangeReport:
        return self._add_element(f"add component '{id}'", Component(id, label, visibility, evolution, decorator))

    def add_anchor(self, id: str, label: str, visibility: float, evolution: float) -> ChangeReport:
        return self._add_element(f"add anchor '{id}'", Component(id, label, visibility, evolution, anchor=True))

    def add_dependency(self, id: str, source_id: str, target_id: str, label: str = "") -> ChangeReport:
        return self._add_relation(f"add dependency '{id}'", Dependency(id, (source_id, target_id), label))

    def add_evolution(self, id: str, component_id: str, target: float) -> ChangeReport:
        return self._add_element(f"add evolution '{id}'", Evolution(id, component_id, target))
