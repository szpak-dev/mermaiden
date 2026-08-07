from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity


@dataclass(frozen=True, slots=True)
class Terminal(Entity):
    kind: ClassVar[str] = "terminal"


@dataclass(frozen=True, slots=True)
class NonTerminal(Entity):
    kind: ClassVar[str] = "nonterminal"


@dataclass(frozen=True, slots=True)
class Sequence(Container):
    kind: ClassVar[str] = "sequence"

