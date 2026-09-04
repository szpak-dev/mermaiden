from enum import StrEnum

from ...core.domain import Relation


class MessageKind(StrEnum):
    SOLID = "solid"
    DOTTED = "dotted"
    OPEN = "open"
    DOTTED_OPEN = "dotted_open"


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


class Message(Relation):
    message_kind: MessageKind = MessageKind.SOLID
    activate: bool = False
    deactivate: bool = False


class ParticipantEvent(Relation):
    action: str = "activate"


class Control(Relation):
    control_kind: ControlKind = ControlKind.END


class Directive(Relation):
    directive_kind: DirectiveKind = DirectiveKind.AUTONUMBER
