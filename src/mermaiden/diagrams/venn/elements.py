from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class VennSet(Container):
    kind: ClassVar[str] = "venn_set"
    size: float | None = None


@dataclass(frozen=True, slots=True)
class VennUnion(Container):
    kind: ClassVar[str] = "venn_union"
    set_ids: tuple[str, ...] = ()
    size: float | None = None


@dataclass(frozen=True, slots=True)
class VennText(Entity):
    kind: ClassVar[str] = "venn_text"
