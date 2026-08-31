from enum import StrEnum

from ...core.domain import Relation


class ClassRelationKind(StrEnum):
    ASSOCIATION = "--"
    INHERITANCE = "<|--"
    COMPOSITION = "*--"
    AGGREGATION = "o--"
    DEPENDENCY = "<.."
    REALIZATION = "<|.."


class ClassRelation(Relation):
    relation_kind: ClassRelationKind = ClassRelationKind.ASSOCIATION
    source_label: str = ""
    target_label: str = ""
