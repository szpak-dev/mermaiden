from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity


@dataclass(frozen=True, slots=True)
class C4Element(Entity):
    description: str = ""
    technology: str = ""


@dataclass(frozen=True, slots=True)
class Person(C4Element):
    kind: ClassVar[str] = "person"


@dataclass(frozen=True, slots=True)
class System(C4Element):
    kind: ClassVar[str] = "system"


@dataclass(frozen=True, slots=True)
class SystemDb(C4Element):
    kind: ClassVar[str] = "systemdb"


@dataclass(frozen=True, slots=True)
class SystemQueue(C4Element):
    kind: ClassVar[str] = "systemqueue"
