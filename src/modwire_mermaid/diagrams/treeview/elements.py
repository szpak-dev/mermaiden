from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity


@dataclass(frozen=True, slots=True)
class TreeItem(Entity):
    kind: ClassVar[str] = "tree_item"
