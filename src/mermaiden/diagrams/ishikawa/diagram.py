from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import IshikawaDiagramConfiguration
from .constraints import IshikawaAnnotationMember, IshikawaDiagramConstraint
from .elements import Category, Cause, Effect, IshikawaElementMember
from .relations import IshikawaRelationMember


@injectable(as_type=DiagramModel, qualifier="ishikawa", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class IshikawaDiagram(DiagramModel):
    constraints: Sequence[IshikawaDiagramConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "ishikawa.member_type",
        IshikawaElementMember,
        IshikawaRelationMember,
        IshikawaAnnotationMember,
    )
    configuration: IshikawaDiagramConfiguration = field(default_factory=IshikawaDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "ishikawa-beta",
        "Ishikawa diagram",
        "ishikawa",
        "IshikawaDiagramConfig",
    )


    def add_effect(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add effect '{id}'", Effect(id, label))

    def add_category(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add category '{id}'", Category(id, label), parent_id)

    def add_cause(self, id: str, label: str, parent_id: str) -> ChangeReport:
        return self._add_element(f"add cause '{id}'", Cause(id, label), parent_id)
