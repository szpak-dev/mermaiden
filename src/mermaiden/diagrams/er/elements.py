from ...core.element import Container
from ...core.element import Entity as EntityNode


class EntityAttribute(EntityNode):
    data_type: str = "string"
    keys: tuple[str, ...] = ()
    comment: str = ""


class Entity(Container):
    pass
