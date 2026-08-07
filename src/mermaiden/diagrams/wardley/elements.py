from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class Component(Entity):
    kind: ClassVar[str] = "component"
    visibility: float = 0
    evolution: float = 0
    decorator: str = ""
    anchor: bool = False


@dataclass(frozen=True, slots=True)
class Evolution(Entity):
    kind: ClassVar[str] = "evolution"
    target: float = 0


@dataclass(frozen=True, slots=True)
class Pipeline(Container):
    kind: ClassVar[str] = "pipeline"
