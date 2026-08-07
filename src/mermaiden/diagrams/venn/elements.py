from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class VennElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a Venn diagram"


@dataclass(frozen=True, slots=True)
class VennSet(Container, VennElementMember):
    kind: ClassVar[str] = "venn_set"
    size: float | None = None


@dataclass(frozen=True, slots=True)
class VennUnion(Container, VennElementMember):
    kind: ClassVar[str] = "venn_union"
    set_ids: tuple[str, ...] = ()
    size: float | None = None


@dataclass(frozen=True, slots=True)
class VennText(Entity, VennElementMember):
    kind: ClassVar[str] = "venn_text"
