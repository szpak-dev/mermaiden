from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.relation import Relation


class RequirementRelationKind(StrEnum):
    CONTAINS = "contains"
    COPIES = "copies"
    DERIVES = "derives"
    SATISFIES = "satisfies"
    VERIFIES = "verifies"
    REFINES = "refines"
    TRACES = "traces"


@dataclass(frozen=True, slots=True)
class RequirementRelation(Relation):
    kind: ClassVar[str] = "requirement_relation"
    relation_kind: RequirementRelationKind = RequirementRelationKind.TRACES

    @property
    def source_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def target_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""
