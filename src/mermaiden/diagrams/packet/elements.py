from ...core.domain import Entity


class PacketField(Entity):
    start: int | None = None
    end: int | None = None
    bits: int | None = None
