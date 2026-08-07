from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar

from ...core.annotation import Annotation, TargetKind, TargetRef
from ...core.error import OperationError
from ..domain import DiagramAnnotationMember


class ArchitectureAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "an architecture note"


@dataclass(frozen=True, slots=True)
class ArchitectureNote(Annotation, ArchitectureAnnotationMember):
    kind: ClassVar[str] = "architecture_note"
    text: str


@dataclass(frozen=True, slots=True)
class ArchitectureNotes:
    def create(
        self, id: str, data: Mapping[str, object], element_ids: Sequence[str], relation_ids: Sequence[str]
    ) -> ArchitectureNote:
        if relation_ids or len(element_ids) != 1 or set(data) != {"text"} or not isinstance(data.get("text"), str):
            raise OperationError("Architecture notes require one element and one string 'text' value.")
        text = data["text"]
        assert isinstance(text, str)
        return ArchitectureNote(id, (TargetRef(TargetKind.ELEMENT, element_ids[0]),), text)
