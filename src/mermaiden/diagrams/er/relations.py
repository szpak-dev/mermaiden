from enum import StrEnum

from ...core.domain import Relation


class Cardinality(StrEnum):
    ZERO_OR_ONE = "zero_or_one"
    EXACTLY_ONE = "exactly_one"
    ZERO_OR_MORE = "zero_or_more"
    ONE_OR_MORE = "one_or_more"


class EntityRelationship(Relation):
    source_cardinality: Cardinality = Cardinality.EXACTLY_ONE
    target_cardinality: Cardinality = Cardinality.EXACTLY_ONE
    identifying: bool = True
