from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity


@dataclass(frozen=True, slots=True)
class PieSlice(Entity):
    kind: ClassVar[str] = "pie_slice"
    value: float = 0
