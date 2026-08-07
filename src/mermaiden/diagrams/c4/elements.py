from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity
from ..domain import DiagramElementMember


class C4ElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in C4 Context diagram"


@dataclass(frozen=True, slots=True)
class C4Element(Entity):
    description: str = ""
    technology: str = ""


@dataclass(frozen=True, slots=True)
class Person(C4Element, C4ElementMember):
    kind: ClassVar[str] = "person"


@dataclass(frozen=True, slots=True)
class System(C4Element, C4ElementMember):
    kind: ClassVar[str] = "system"


@dataclass(frozen=True, slots=True)
class SystemDb(C4Element, C4ElementMember):
    kind: ClassVar[str] = "systemdb"


@dataclass(frozen=True, slots=True)
class SystemQueue(C4Element, C4ElementMember):
    kind: ClassVar[str] = "systemqueue"
