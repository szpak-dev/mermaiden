from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container
from ...core.element import Entity as EntityNode


@dataclass(frozen=True, slots=True)
class EntityAttribute(EntityNode):
    kind: ClassVar[str] = "entityattribute"
    data_type: str = "string"
    keys: tuple[str, ...] = ()
    comment: str = ""


@dataclass(frozen=True, slots=True)
class Entity(Container):
    kind: ClassVar[str] = "entity"
