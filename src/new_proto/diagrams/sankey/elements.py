from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity


@dataclass(frozen=True, slots=True)
class SankeyNode(Entity):
    kind: ClassVar[str] = "sankey_node"
