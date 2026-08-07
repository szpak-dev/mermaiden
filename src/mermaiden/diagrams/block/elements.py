from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class BlockGroup(Container):
    kind: ClassVar[str] = "block_group"
    columns: int | None = None
    span: int | None = None


@dataclass(frozen=True, slots=True)
class BlockNode(Entity):
    kind: ClassVar[str] = "block_node"
    span: int | None = None


@dataclass(frozen=True, slots=True)
class BlockSpace(Entity):
    kind: ClassVar[str] = "block_space"
    span: int | None = None
