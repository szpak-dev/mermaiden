
from ...core.element import Entity


class C4Element(Entity):
    description: str = ""
    technology: str = ""


class Person(C4Element):
    pass


class System(C4Element):
    pass


class SystemDb(C4Element):
    pass


class SystemQueue(C4Element):
    pass
