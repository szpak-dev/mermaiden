from dataclasses import dataclass
from typing import ClassVar

from ...core.relation import Relation


@dataclass(frozen=True, slots=True)
class SankeyLink(Relation):
    kind: ClassVar[str] = "sankey_link"
    value: float = 0

    @property
    def source_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def target_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""
