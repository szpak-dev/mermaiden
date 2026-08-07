from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class ArchitectureElementMember(DiagramElementMember):
    description: ClassVar[str] = "an architecture member"


@dataclass(frozen=True, slots=True)
class ArchitectureGroup(Container, ArchitectureElementMember):
    kind: ClassVar[str] = "architecture_group"
    columns: int = 1


@dataclass(frozen=True, slots=True)
class Service(Entity, ArchitectureElementMember):
    kind: ClassVar[str] = "service"


@dataclass(frozen=True, slots=True)
class Junction(Entity, ArchitectureElementMember):
    kind: ClassVar[str] = "junction"
