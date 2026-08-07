from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..base import DiagramModel
from .annotations import NotePosition, SequenceNotes
from .constraints import SequenceConstraint
from .elements import Participant, ParticipantBox, ParticipantKind
from .relations import Control, ControlKind, Directive, DirectiveKind, Message, MessageKind, ParticipantEvent


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SequenceDiagram(DiagramModel):
    constraints: Sequence[SequenceConstraint]
    syntax: ClassVar[str] = "sequenceDiagram"

    def add_box(self, id: str, label: str, color: str = "") -> ChangeReport:
        return self._add_element(f"add box '{id}'", ParticipantBox(id, label, (), color))

    def add_participant(
        self, id: str, label: str = "", kind: ParticipantKind = ParticipantKind.PARTICIPANT, box_id: str = ""
    ) -> ChangeReport:
        return self._add_element(f"add participant '{id}'", Participant(id, label or id, kind), box_id)

    def add_message(
        self,
        id: str,
        source_id: str,
        target_id: str,
        label: str,
        kind: MessageKind = MessageKind.SOLID,
        activate: bool = False,
        deactivate: bool = False,
    ) -> ChangeReport:
        return self._add_relation(
            f"add message '{id}'", Message(id, (source_id, target_id), label, kind, activate, deactivate)
        )

    def activate(self, id: str, participant_id: str) -> ChangeReport:
        return self._event(id, participant_id, "activate")

    def deactivate(self, id: str, participant_id: str) -> ChangeReport:
        return self._event(id, participant_id, "deactivate")

    def create(self, id: str, participant_id: str) -> ChangeReport:
        return self._event(id, participant_id, "create")

    def destroy(self, id: str, participant_id: str) -> ChangeReport:
        return self._event(id, participant_id, "destroy")

    def control(self, id: str, kind: ControlKind, label: str = "") -> ChangeReport:
        return self._add_relation(
            f"add {kind.value} '{id}'",
            Control(id, self._anchors(f"add {kind.value} '{id}'"), label, kind),
        )

    def autonumber(self, id: str) -> ChangeReport:
        return self._add_relation(
            f"add autonumber '{id}'",
            Directive(id, self._anchors(f"add autonumber '{id}'"), "", DirectiveKind.AUTONUMBER),
        )

    def add_note(
        self, id: str, text: str, *participant_ids: str, position: NotePosition = NotePosition.OVER
    ) -> ChangeReport:
        return self._annotate(
            f"add note '{id}'",
            SequenceNotes(),
            id,
            {"text": text, "position": position},
            participant_ids,
        )

    def _event(self, id: str, participant_id: str, action: str) -> ChangeReport:
        return self._add_relation(
            f"{action} '{participant_id}'",
            ParticipantEvent(id, (participant_id, participant_id), "", action),
        )

    def _anchors(self, operation: str) -> tuple[str, str]:
        participants = [item.id for item in self.walk_elements() if isinstance(item, Participant)]
        if len(participants) < 2:
            self._reject(operation, "Sequence directives require two participants.")
        return participants[0], participants[1]
