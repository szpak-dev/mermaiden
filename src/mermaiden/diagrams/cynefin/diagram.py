from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import CynefinDiagramConfiguration
from .constraints import CynefinAnnotationMember, CynefinDiagramConstraint
from .elements import CynefinElementMember, Domain, DomainKind
from .relations import CynefinRelationMember, Transition


@injectable(as_type=DiagramModel, qualifier="cynefin", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class CynefinDiagram(DiagramModel):
    constraints: Sequence[CynefinDiagramConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "cynefin.member_type",
        CynefinElementMember,
        CynefinRelationMember,
        CynefinAnnotationMember,
    )
    configuration: CynefinDiagramConfiguration = field(default_factory=CynefinDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "cynefin-beta",
        "Cynefin diagram",
        "cynefin",
        "CynefinDiagramConfig",
    )


    def add_item(self, id: str, label: str, domain: DomainKind) -> ChangeReport:
        return self._add_element(f"add {domain.value} item '{id}'", Domain(id, label, domain))

    def add_transition(self, id: str, source_id: str, target_id: str, label: str = "") -> ChangeReport:
        return self._add_relation(f"add transition '{id}'", Transition(id, (source_id, target_id), label))
