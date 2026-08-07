from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class IshikawaRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in Ishikawa diagram"


@dataclass(frozen=True, slots=True)
class CauseRelation(Relation, IshikawaRelationMember):
    kind: ClassVar[str] = "causerelation"

