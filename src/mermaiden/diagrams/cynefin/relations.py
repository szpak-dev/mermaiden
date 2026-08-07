from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class CynefinRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in Cynefin diagram"


@dataclass(frozen=True, slots=True)
class Transition(Relation, CynefinRelationMember):
    kind: ClassVar[str] = "transition"
