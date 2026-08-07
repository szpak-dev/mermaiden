from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ConstraintLevel, Violation
from ...core.diagram import Diagram
from .annotations import SequenceNote
from .elements import Participant, ParticipantBox
from .relations import Control, Directive, Message, ParticipantEvent


class SequenceConstraint(Constraint):
    pass


@injectable(as_type=SequenceConstraint, qualifier="sequence_members")
@dataclass(frozen=True, slots=True)
class SequenceMembers(SequenceConstraint):
    @property
    def code(self) -> str:
        return "sequence.members"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        members = Participant | ParticipantBox
        relations = Message | ParticipantEvent | Control | Directive
        issues = [
            self.violation(f"Element '{item.id}' is not a sequence member.")
            for item in diagram.walk_elements()
            if not isinstance(item, members)
        ]
        issues.extend(
            self.violation(f"Relation '{item.id}' is not a sequence event.")
            for item in diagram.find_relations()
            if not isinstance(item, relations)
        )
        issues.extend(
            self.violation(f"Annotation '{item.id}' is not a sequence note.")
            for item in diagram.find_annotations()
            if not isinstance(item, SequenceNote)
        )
        return tuple(issues)
