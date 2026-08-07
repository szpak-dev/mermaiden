from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class ArchitectureGroup(Container):
    kind: ClassVar[str] = "architecture_group"
    columns: int = 1


@dataclass(frozen=True, slots=True)
class Service(Entity):
    kind: ClassVar[str] = "service"


@dataclass(frozen=True, slots=True)
class Junction(Entity):
    kind: ClassVar[str] = "junction"
