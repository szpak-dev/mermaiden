from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class SankeyRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "a Sankey link"


@dataclass(frozen=True, slots=True)
class SankeyLink(Relation, SankeyRelationMember):
    kind: ClassVar[str] = "sankey_link"
    value: float = 0

    @property
    def source_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def target_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""
