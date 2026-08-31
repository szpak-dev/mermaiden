from ...core.domain import Container, Entity


class JourneySection(Container):
    pass


class JourneyTask(Entity):
    score: int = 1
    actors: tuple[str, ...] = ()
