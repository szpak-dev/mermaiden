from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation


@dataclass(frozen=True, slots=True)
class EntityRelationship(Relation):
    kind: ClassVar[str] = "entityrelationship"
    notation: str = "||--||"
