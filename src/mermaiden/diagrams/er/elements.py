from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container
from ...core.element import Entity as EntityNode
from ..domain import DiagramElementMember


class EntityRelationshipElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in an ER diagram"


@dataclass(frozen=True, slots=True)
class EntityAttribute(EntityNode, EntityRelationshipElementMember):
    kind: ClassVar[str] = "entityattribute"
    data_type: str = "string"
    keys: tuple[str, ...] = ()
    comment: str = ""


@dataclass(frozen=True, slots=True)
class Entity(Container, EntityRelationshipElementMember):
    kind: ClassVar[str] = "entity"
