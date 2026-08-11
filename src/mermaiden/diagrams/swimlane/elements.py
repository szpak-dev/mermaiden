
from ...core.element import Container, Entity


class Swimlane(Container):
    pass


class SwimlaneNode(Entity):
    pass


class Activity(SwimlaneNode):
    pass


class Start(SwimlaneNode):
    pass


class End(SwimlaneNode):
    pass


class Decision(SwimlaneNode):
    pass


class Connector(SwimlaneNode):
    pass
