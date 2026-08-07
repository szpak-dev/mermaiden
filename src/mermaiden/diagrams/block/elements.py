from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class BlockElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a block diagram"


@dataclass(frozen=True, slots=True)
class BlockGroup(Container, BlockElementMember):
    kind: ClassVar[str] = "block_group"
    columns: int | None = None
    span: int | None = None


@dataclass(frozen=True, slots=True)
class BlockNode(Entity, BlockElementMember):
    kind: ClassVar[str] = "block_node"
    span: int | None = None


@dataclass(frozen=True, slots=True)
class BlockSpace(Entity, BlockElementMember):
    kind: ClassVar[str] = "block_space"
    span: int | None = None
