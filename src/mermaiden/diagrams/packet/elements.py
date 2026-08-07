from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity
from ..domain import DiagramElementMember


class PacketElementMember(DiagramElementMember):
    description: ClassVar[str] = "a packet field"


@dataclass(frozen=True, slots=True)
class PacketField(Entity, PacketElementMember):
    kind: ClassVar[str] = "packet_field"
    start: int | None = None
    end: int | None = None
    bits: int | None = None
