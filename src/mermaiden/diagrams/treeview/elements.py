from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity
from ..domain import DiagramElementMember


class TreeViewElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a Tree View"


@dataclass(frozen=True, slots=True)
class TreeItem(Entity, TreeViewElementMember):
    kind: ClassVar[str] = "tree_item"
