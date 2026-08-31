from ...core import domain


class EntityAttribute(domain.Entity):
    data_type: str = "string"
    keys: tuple[str, ...] = ()
    comment: str = ""


class Entity(domain.Container):
    pass
