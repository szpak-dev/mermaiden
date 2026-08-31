from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.domain import ChangeReport, Container, Element
from ..domain import DiagramDefinition, DiagramModel
from .configuration import WardleyDiagramConfiguration
from .constraints import WardleyDiagramConstraint
from .elements import Component, Evolution, Pipeline
from .relations import Dependency


@injectable(as_type=DiagramModel, qualifier="wardley", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class WardleyDiagram(DiagramModel):
    constraints: Sequence[WardleyDiagramConstraint]
    configuration: WardleyDiagramConfiguration = field(default_factory=WardleyDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "wardley-beta",
        "Wardley map",
        "wardley-beta",
        "WardleyDiagramConfig",
    )

    def accepts_parent(self, element_type: type[Element], parent_type: type[Container] | None) -> bool:
        return element_type in (Component, Evolution, Pipeline) and parent_type is None

    def add_component(
        self, id: str, label: str, visibility: float, evolution: float, decorator: str = ""
    ) -> ChangeReport:
        return self._add_element(
            f"add component '{id}'",
            Component(id=id, label=label, visibility=visibility, evolution=evolution, decorator=decorator),
        )

    def add_anchor(self, id: str, label: str, visibility: float, evolution: float) -> ChangeReport:
        return self._add_element(
            f"add anchor '{id}'", Component(id=id, label=label, visibility=visibility, evolution=evolution, anchor=True)
        )

    def add_dependency(self, id: str, source_id: str, target_id: str, label: str = "") -> ChangeReport:
        return self._add_relation(
            f"add dependency '{id}'", Dependency(id=id, element_ids=(source_id, target_id), label=label)
        )

    def add_evolution(self, id: str, component_id: str, target: float) -> ChangeReport:
        return self._add_element(f"add evolution '{id}'", Evolution(id=id, label=component_id, target=target))
