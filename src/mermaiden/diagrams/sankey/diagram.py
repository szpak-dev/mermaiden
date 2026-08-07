from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import SankeyDiagramConfiguration
from .constraints import SankeyConstraint
from .elements import SankeyNode
from .relations import SankeyLink


@injectable(as_type=DiagramModel, qualifier="sankey", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Sankey(DiagramModel):
    constraints: Sequence[SankeyConstraint]
    configuration: SankeyDiagramConfiguration = field(default_factory=SankeyDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "sankey"
    name: ClassVar[str] = "Sankey diagram"
    config_key: ClassVar[str] = "sankey"
    schema_definition: ClassVar[str] = "SankeyDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

    def add_node(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add node '{id}'", SankeyNode(id, label))

    def add_flow(self, id: str, source_id: str, target_id: str, value: float) -> ChangeReport:
        return self._add_relation(f"add flow '{id}'", SankeyLink(id, (source_id, target_id), "", value))
