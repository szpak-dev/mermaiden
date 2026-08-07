from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class RailroadElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in Railroad diagram"


@dataclass(frozen=True, slots=True)
class Terminal(Entity, RailroadElementMember):
    kind: ClassVar[str] = "terminal"


@dataclass(frozen=True, slots=True)
class NonTerminal(Entity, RailroadElementMember):
    kind: ClassVar[str] = "nonterminal"


@dataclass(frozen=True, slots=True)
class Special(Entity, RailroadElementMember):
    kind: ClassVar[str] = "special"


@dataclass(frozen=True, slots=True)
class Sequence(Container, RailroadElementMember):
    kind: ClassVar[str] = "sequence"


@dataclass(frozen=True, slots=True)
class Alternative(Container, RailroadElementMember):
    kind: ClassVar[str] = "alternative"


@dataclass(frozen=True, slots=True)
class Optional(Container, RailroadElementMember):
    kind: ClassVar[str] = "optional"


@dataclass(frozen=True, slots=True)
class Repetition(Container, RailroadElementMember):
    kind: ClassVar[str] = "repetition"


@dataclass(frozen=True, slots=True)
class Group(Container, RailroadElementMember):
    kind: ClassVar[str] = "group"
