from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .configuration import MindmapDiagramConfiguration
from .constraints.constraint import MindmapConstraint
from .elements import Bang, Circle, Cloud, Hexagon, MindmapNode, RoundedSquare, Square


@injectable(as_type=DiagramModel, qualifier="mindmap", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Mindmap(DiagramModel):
    constraints: Sequence[MindmapConstraint]
    configuration: MindmapDiagramConfiguration = field(default_factory=MindmapDiagramConfiguration, init=False)
    syntax: ClassVar[str] = "mindmap"
    name: ClassVar[str] = "Mindmap"
    config_key: ClassVar[str] = "mindmap"
    schema_definition: ClassVar[str] = "MindmapDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}

    def add_root(self, id: str, label: str) -> ChangeReport:
        return self._add_node(MindmapNode(id, label), "", "root")

    def add_node(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_node(MindmapNode(id, label), parent_id, "node")

    def add_square(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_node(Square(id, label), parent_id, "square")

    def add_rounded_square(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_node(RoundedSquare(id, label), parent_id, "rounded square")

    def add_circle(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_node(Circle(id, label), parent_id, "circle")

    def add_bang(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_node(Bang(id, label), parent_id, "bang")

    def add_cloud(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_node(Cloud(id, label), parent_id, "cloud")

    def add_hexagon(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_node(Hexagon(id, label), parent_id, "hexagon")

    def _add_node(self, node: MindmapNode, parent_id: str, kind: str) -> ChangeReport:
        return self._add_element(f"add {kind} '{node.id}'", node, parent_id)
