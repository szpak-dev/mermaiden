from ...core.element import Container, Entity


class Task(Entity):
    metadata: tuple[str, ...] = ()


class Milestone(Entity):
    metadata: tuple[str, ...] = ()


class Marker(Entity):
    date: str = ""


class Section(Container):
    pass
