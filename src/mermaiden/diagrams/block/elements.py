from ...core.element import Container, Entity


class BlockGroup(Container):
    columns: int | None = None
    span: int | None = None


class BlockNode(Entity):
    span: int | None = None


class BlockSpace(Entity):
    span: int | None = None
