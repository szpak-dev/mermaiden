from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class WardleyElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in Wardley map"


@dataclass(frozen=True, slots=True)
class Component(Entity, WardleyElementMember):
    kind: ClassVar[str] = "component"
    visibility: float = 0
    evolution: float = 0
    decorator: str = ""
    anchor: bool = False


@dataclass(frozen=True, slots=True)
class Evolution(Entity, WardleyElementMember):
    kind: ClassVar[str] = "evolution"
    target: float = 0


@dataclass(frozen=True, slots=True)
class Pipeline(Container, WardleyElementMember):
    kind: ClassVar[str] = "pipeline"
