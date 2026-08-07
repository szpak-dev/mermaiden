from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.element import Entity


class RequirementType(StrEnum):
    REQUIREMENT = "requirement"
    FUNCTIONAL = "functionalRequirement"
    INTERFACE = "interfaceRequirement"
    PERFORMANCE = "performanceRequirement"
    PHYSICAL = "physicalRequirement"
    DESIGN_CONSTRAINT = "designConstraint"


class Risk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class VerificationMethod(StrEnum):
    ANALYSIS = "analysis"
    INSPECTION = "inspection"
    TEST = "test"
    DEMONSTRATION = "demonstration"


@dataclass(frozen=True, slots=True)
class Requirement(Entity):
    kind: ClassVar[str] = "requirement"
    requirement_id: str = ""
    text: str = ""
    requirement_type: RequirementType = RequirementType.REQUIREMENT
    risk: Risk = Risk.MEDIUM
    verification_method: VerificationMethod = VerificationMethod.ANALYSIS


@dataclass(frozen=True, slots=True)
class RequirementElement(Entity):
    kind: ClassVar[str] = "requirement_element"
    element_type: str = ""
    document_reference: str = ""
