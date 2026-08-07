from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class EventModelingRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in Event Modeling diagram"


@dataclass(frozen=True, slots=True)
class Flow(Relation, EventModelingRelationMember):
    kind: ClassVar[str] = "flow"

