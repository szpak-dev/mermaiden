from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity
from ..domain import DiagramElementMember


class SankeyElementMember(DiagramElementMember):
    description: ClassVar[str] = "a Sankey node"


@dataclass(frozen=True, slots=True)
class SankeyNode(Entity, SankeyElementMember):
    kind: ClassVar[str] = "sankey_node"
