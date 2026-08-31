from enum import StrEnum

from ...core.domain import Relation


class RequirementRelationKind(StrEnum):
    CONTAINS = "contains"
    COPIES = "copies"
    DERIVES = "derives"
    SATISFIES = "satisfies"
    VERIFIES = "verifies"
    REFINES = "refines"
    TRACES = "traces"


class RequirementRelation(Relation):
    relation_kind: RequirementRelationKind = RequirementRelationKind.TRACES
