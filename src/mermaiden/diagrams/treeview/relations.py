from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class TreeViewRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "a tree branch"


@dataclass(frozen=True, slots=True)
class TreeBranch(Relation, TreeViewRelationMember):
    kind: ClassVar[str] = "tree_branch"

    @property
    def parent_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def child_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""
