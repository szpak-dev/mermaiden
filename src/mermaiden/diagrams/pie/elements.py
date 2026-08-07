from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity
from ..domain import DiagramElementMember


class PieElementMember(DiagramElementMember):
    description: ClassVar[str] = "a pie slice"


@dataclass(frozen=True, slots=True)
class PieSlice(Entity, PieElementMember):
    kind: ClassVar[str] = "pie_slice"
    value: float = 0
