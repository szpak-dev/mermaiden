from enum import StrEnum

from ...core.domain import Relation


class ClassRelationKind(StrEnum):
    ASSOCIATION = "association"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    DEPENDENCY = "dependency"
    REALIZATION = "realization"


class ClassRelation(Relation):
    relation_kind: ClassRelationKind = ClassRelationKind.ASSOCIATION
    source_label: str = ""
    target_label: str = ""
