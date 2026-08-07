from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class C4RelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in C4 Context diagram"


@dataclass(frozen=True, slots=True)
class Relationship(Relation, C4RelationMember):
    kind: ClassVar[str] = "relationship"

