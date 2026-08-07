from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.relation import Relation


class Port(StrEnum):
    TOP = "T"
    RIGHT = "R"
    BOTTOM = "B"
    LEFT = "L"


@dataclass(frozen=True, slots=True)
class Edge(Relation):
    kind: ClassVar[str] = "edge"
    source_port: Port = Port.RIGHT
    target_port: Port = Port.LEFT

    @property
    def source_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def target_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""
