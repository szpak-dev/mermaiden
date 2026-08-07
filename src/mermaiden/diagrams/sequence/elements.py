from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.element import Container, Entity


class ParticipantKind(StrEnum):
    PARTICIPANT = "participant"
    ACTOR = "actor"
    BOUNDARY = "boundary"
    CONTROL = "control"
    ENTITY = "entity"
    DATABASE = "database"
    COLLECTIONS = "collections"
    QUEUE = "queue"


@dataclass(frozen=True, slots=True)
class Participant(Entity):
    kind: ClassVar[str] = "participant"
    participant_kind: ParticipantKind = ParticipantKind.PARTICIPANT
    created: bool = False


@dataclass(frozen=True, slots=True)
class ParticipantBox(Container):
    kind: ClassVar[str] = "participant_box"
    color: str = ""
