
from enum import StrEnum

from ...core.relation import Relation


class RelationshipDirection(StrEnum):
    DEFAULT = "Rel"
    RIGHT = "Rel_R"
    LEFT = "Rel_L"
    UP = "Rel_Up"
    DOWN = "Rel_Down"


class Relationship(Relation):
    direction: RelationshipDirection = RelationshipDirection.DEFAULT
