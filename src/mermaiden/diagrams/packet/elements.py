from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity


@dataclass(frozen=True, slots=True)
class PacketField(Entity):
    kind: ClassVar[str] = "packet_field"
    start: int | None = None
    end: int | None = None
    bits: int | None = None
