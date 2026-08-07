from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.annotation import Annotation, TargetKind, TargetRef
from ...core.error import OperationError
from ..domain import DiagramAnnotationMember


class StateAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "a state note"


class NotePosition(StrEnum):
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True, slots=True)
class StateNote(Annotation, StateAnnotationMember):
    kind: ClassVar[str] = "state_note"
    text: str
    position: NotePosition
    scope_id: str = ""


@dataclass(frozen=True, slots=True)
class StateNotes:
    def create(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str],
        relation_ids: Sequence[str],
    ) -> StateNote:
        if relation_ids or len(element_ids) != 1:
            raise OperationError("State notes target exactly one state node.")
        if set(data) != {"text", "position", "scope_id"}:
            raise OperationError("State notes require text, position, and scope.")
        text = data["text"]
        position = data["position"]
        scope_id = data["scope_id"]
        if not isinstance(text, str) or not isinstance(position, NotePosition) or not isinstance(scope_id, str):
            raise OperationError("State note data is invalid.")
        return StateNote(id, (TargetRef(TargetKind.ELEMENT, element_ids[0]),), text, position, scope_id)
