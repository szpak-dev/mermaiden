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
class Special(Entity):
    kind: ClassVar[str] = "special"


@dataclass(frozen=True, slots=True)
class Sequence(Container):
    kind: ClassVar[str] = "sequence"


@dataclass(frozen=True, slots=True)
class Alternative(Container):
    kind: ClassVar[str] = "alternative"


@dataclass(frozen=True, slots=True)
class Optional(Container):
    kind: ClassVar[str] = "optional"


@dataclass(frozen=True, slots=True)
class Repetition(Container):
    kind: ClassVar[str] = "repetition"


@dataclass(frozen=True, slots=True)
class Group(Container):
    kind: ClassVar[str] = "group"
