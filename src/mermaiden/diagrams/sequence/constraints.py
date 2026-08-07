from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint
from ..domain import DiagramMembersConstraint
from .annotations import SequenceNote
from .elements import Participant, ParticipantBox
from .relations import Control, Directive, Message, ParticipantEvent


class SequenceConstraint(Constraint):
    pass


@injectable(as_type=SequenceConstraint, qualifier="sequence_members")
class SequenceMembers(DiagramMembersConstraint, SequenceConstraint):
    element_types: ClassVar = (Participant, ParticipantBox)
    relation_types: ClassVar = (Message, ParticipantEvent, Control, Directive)
    annotation_types: ClassVar = (SequenceNote,)
    element_description: ClassVar[str] = "a sequence member"
    relation_description: ClassVar[str] = "a sequence event"
    annotation_description: ClassVar[str] = "a sequence note"

    @property
    def code(self) -> str:
        return "sequence.members"
