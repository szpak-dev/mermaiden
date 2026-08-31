from enum import StrEnum

from ...core.domain import Entity


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


class RequirementEndpoint:
    pass


class Requirement(Entity, RequirementEndpoint):
    requirement_id: str = ""
    text: str = ""
    requirement_type: RequirementType = RequirementType.REQUIREMENT
    risk: Risk = Risk.MEDIUM
    verification_method: VerificationMethod = VerificationMethod.ANALYSIS


class RequirementElement(Entity, RequirementEndpoint):
    element_type: str = ""
    document_reference: str = ""
