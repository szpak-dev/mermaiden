
from ...core.element import Container, Entity


class VennSet(Container):
    size: float | None = None


class VennUnion(Container):
    set_ids: tuple[str, ...] = ()
    size: float | None = None


class VennText(Entity):
    pass
