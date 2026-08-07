from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class SequenceRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "a sequence event"


class MessageKind(StrEnum):
    SOLID = "->>"
    DOTTED = "-->>"
    OPEN = "-)"
    DOTTED_OPEN = "--)"


class ControlKind(StrEnum):
    LOOP = "loop"
    ALT = "alt"
    ELSE = "else"
    OPT = "opt"
    PAR = "par"
    AND = "and"
    CRITICAL = "critical"
    OPTION = "option"
    BREAK = "break"
    RECT = "rect"
    END = "end"


class DirectiveKind(StrEnum):
    AUTONUMBER = "autonumber"


@dataclass(frozen=True, slots=True)
class Message(Relation, SequenceRelationMember):
    kind: ClassVar[str] = "message"
    message_kind: MessageKind = MessageKind.SOLID
    activate: bool = False
    deactivate: bool = False

    @property
    def source_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def target_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""


@dataclass(frozen=True, slots=True)
class ParticipantEvent(Relation, SequenceRelationMember):
    kind: ClassVar[str] = "participant_event"
    action: str = "activate"


@dataclass(frozen=True, slots=True)
class Control(Relation, SequenceRelationMember):
    kind: ClassVar[str] = "control"
    control_kind: ControlKind = ControlKind.END


@dataclass(frozen=True, slots=True)
class Directive(Relation, SequenceRelationMember):
    kind: ClassVar[str] = "directive"
    directive_kind: DirectiveKind = DirectiveKind.AUTONUMBER
