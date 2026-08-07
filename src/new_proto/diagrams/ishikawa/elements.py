from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class Effect(Entity):
    kind: ClassVar[str] = "effect"


@dataclass(frozen=True, slots=True)
class Cause(Entity):
    kind: ClassVar[str] = "cause"


@dataclass(frozen=True, slots=True)
class Category(Container):
    kind: ClassVar[str] = "category"

