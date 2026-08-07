from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramModel
from .configuration import RequirementDiagramConfiguration
from .constraints import RequirementDiagramConstraint
from .elements import (
    Requirement,
    RequirementElement,
    RequirementType,
    Risk,
    VerificationMethod,
)
from .relations import RequirementRelation, RequirementRelationKind


@injectable(as_type=DiagramModel, qualifier="requirement", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class RequirementDiagram(DiagramModel):
    constraints: Sequence[RequirementDiagramConstraint]
    configuration: RequirementDiagramConfiguration = field(default_factory=RequirementDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "requirementDiagram",
        "Requirement diagram",
        "requirement",
        "RequirementDiagramConfig",
    )


    def add_requirement(
        self,
        id: str,
        requirement_id: str,
        text: str,
        requirement_type: RequirementType = RequirementType.REQUIREMENT,
        risk: Risk = Risk.MEDIUM,
        verification_method: VerificationMethod = VerificationMethod.ANALYSIS,
    ) -> ChangeReport:
        return self._add_element(
            f"add requirement '{id}'",
            Requirement(id, id, requirement_id, text, requirement_type, risk, verification_method),
        )

    def add_element(self, id: str, element_type: str, document_reference: str) -> ChangeReport:
        return self._add_element(
            f"add element '{id}'",
            RequirementElement(id, id, element_type, document_reference),
        )

    def add_relation(
        self,
        id: str,
        source_id: str,
        target_id: str,
        relation_kind: RequirementRelationKind,
    ) -> ChangeReport:
        return self._add_relation(
            f"add {relation_kind.value} relation '{id}'",
            RequirementRelation(id, (source_id, target_id), "", relation_kind),
        )

    def remove_relation(self, id: str) -> ChangeReport:
        return super().remove_relation(id)
