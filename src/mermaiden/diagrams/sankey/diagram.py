from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import SankeyDiagramConfiguration
from .constraints import SankeyAnnotationMember, SankeyConstraint
from .elements import SankeyElementMember, SankeyNode
from .relations import SankeyLink, SankeyRelationMember


@injectable(as_type=DiagramModel, qualifier="sankey", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Sankey(DiagramModel):
    constraints: Sequence[SankeyConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "sankey.member_type",
        SankeyElementMember,
        SankeyRelationMember,
        SankeyAnnotationMember,
    )
    configuration: SankeyDiagramConfiguration = field(default_factory=SankeyDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "sankey",
        "Sankey diagram",
        "sankey",
        "SankeyDiagramConfig",
    )


    def add_node(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add node '{id}'", SankeyNode(id, label))

    def add_flow(self, id: str, source_id: str, target_id: str, value: float) -> ChangeReport:
        return self._add_relation(f"add flow '{id}'", SankeyLink(id, (source_id, target_id), "", value))
