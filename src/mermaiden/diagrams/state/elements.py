from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class StateElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a state diagram"


@dataclass(frozen=True, slots=True)
class StateNode(Entity, StateElementMember):
    kind: ClassVar[str] = "state_node"


@dataclass(frozen=True, slots=True)
class State(StateNode):
    kind: ClassVar[str] = "state"


@dataclass(frozen=True, slots=True)
class Initial(StateNode):
    kind: ClassVar[str] = "initial"


@dataclass(frozen=True, slots=True)
class Final(StateNode):
    kind: ClassVar[str] = "final"


@dataclass(frozen=True, slots=True)
class Choice(StateNode):
    kind: ClassVar[str] = "choice"


@dataclass(frozen=True, slots=True)
class Fork(StateNode):
    kind: ClassVar[str] = "fork"


@dataclass(frozen=True, slots=True)
class Join(StateNode):
    kind: ClassVar[str] = "join"


@dataclass(frozen=True, slots=True)
class CompositeState(Container, StateElementMember):
    kind: ClassVar[str] = "composite_state"

