from enum import StrEnum

from ...core.domain import Container, Entity


class ParticipantKind(StrEnum):
    PARTICIPANT = "participant"
    ACTOR = "actor"
    BOUNDARY = "boundary"
    CONTROL = "control"
    ENTITY = "entity"
    DATABASE = "database"
    COLLECTIONS = "collections"
    QUEUE = "queue"


class Participant(Entity):
    participant_kind: ParticipantKind = ParticipantKind.PARTICIPANT
    created: bool = False


class ParticipantBox(Container):
    color: str = ""
