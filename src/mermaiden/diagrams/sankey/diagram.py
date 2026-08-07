from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport, Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint, DiagramModel
from .elements import SankeyNode
from .relations import SankeyLink


class SankeyConstraint(Constraint):
    @property
    def code(self) -> str:
        return "sankey.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()


@injectable(as_type=SankeyConstraint, qualifier="sankey_structure")
class SankeyStructure(SankeyConstraint):
    pass


@injectable(as_type=SankeyConstraint, qualifier="sankey_members")
class SankeyMembers(DiagramMembersConstraint, SankeyConstraint):
    element_types: ClassVar = (SankeyNode,)
    relation_types: ClassVar = (SankeyLink,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "a Sankey node"
    relation_description: ClassVar[str] = "a Sankey link"
    annotation_description: ClassVar[str] = "valid in a Sankey diagram"

    @property
    def code(self) -> str:
        return "sankey.member_type"


@injectable(as_type=DiagramModel, qualifier="sankey", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Sankey(DiagramModel):
    constraints: Sequence[SankeyConstraint]
    syntax: ClassVar[str] = "sankey"
    name: ClassVar[str] = "Sankey diagram"
    config_key: ClassVar[str] = "sankey"
    schema_definition: ClassVar[str] = "SankeyDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {}

    def add_node(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add node '{id}'", SankeyNode(id, label))

    def add_flow(self, id: str, source_id: str, target_id: str, value: float) -> ChangeReport:
        return self._add_relation(f"add flow '{id}'", SankeyLink(id, (source_id, target_id), "", value))
