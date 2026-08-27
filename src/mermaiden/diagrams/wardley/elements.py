from ...core.element import Container, Entity


class Component(Entity):
    visibility: float = 0
    evolution: float = 0
    decorator: str = ""
    anchor: bool = False


class Evolution(Entity):
    target: float = 0


class Pipeline(Container):
    pass
