from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class EntityRelationshipRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in an ER diagram"


@dataclass(frozen=True, slots=True)
class EntityRelationship(Relation, EntityRelationshipRelationMember):
    kind: ClassVar[str] = "entityrelationship"
    notation: str = "||--||"
