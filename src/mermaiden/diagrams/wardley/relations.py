from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class WardleyRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in Wardley map"


@dataclass(frozen=True, slots=True)
class Dependency(Relation, WardleyRelationMember):
    kind: ClassVar[str] = "dependency"
    operator: str = "->"
