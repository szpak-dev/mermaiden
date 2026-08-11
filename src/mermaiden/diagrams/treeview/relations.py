
from ...core.relation import Relation


class TreeBranch(Relation):

    @property
    def parent_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def child_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""
