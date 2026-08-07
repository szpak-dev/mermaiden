
from ...core.element import Container, Entity


class SwimlaneMember:
    pass


class Event(Entity, SwimlaneMember):
    pass


class Command(Entity, SwimlaneMember):
    pass


class View(Entity, SwimlaneMember):
    pass


class Actor(Entity, SwimlaneMember):
    pass


class Swimlane(Container):
    pass
