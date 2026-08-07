from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class StateRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "a state transition"


@dataclass(frozen=True, slots=True)
class StateTransition(Relation, StateRelationMember):
    kind: ClassVar[str] = "state_transition"
    scope_id: str = ""
    source_terminal: bool = False
    target_terminal: bool = False

    @property
    def source_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def target_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""
