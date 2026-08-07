from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class IshikawaElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in Ishikawa diagram"


@dataclass(frozen=True, slots=True)
class Effect(Entity, IshikawaElementMember):
    kind: ClassVar[str] = "effect"


@dataclass(frozen=True, slots=True)
class Cause(Entity, IshikawaElementMember):
    kind: ClassVar[str] = "cause"


@dataclass(frozen=True, slots=True)
class Category(Container, IshikawaElementMember):
    kind: ClassVar[str] = "category"

