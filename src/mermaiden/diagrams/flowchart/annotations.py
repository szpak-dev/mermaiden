from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar

from ...core.annotation import Annotation, TargetKind, TargetRef
from ...core.error import OperationError
from ..domain import DiagramAnnotationMember


class FlowchartAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "a flowchart note"


@dataclass(frozen=True, slots=True)
class Note(Annotation, FlowchartAnnotationMember):
    kind: ClassVar[str] = "note"
    text: str


@dataclass(frozen=True, slots=True)
class Notes:
    def create(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str],
        relation_ids: Sequence[str],
    ) -> Note:
        if relation_ids:
            raise OperationError("Flowchart notes can only target elements.")
        if set(data) != {"text"} or not isinstance(data.get("text"), str):
            raise OperationError("Flowchart notes require exactly one string 'text' value.")
        text = data["text"]
        assert isinstance(text, str)
        targets = tuple(TargetRef(TargetKind.ELEMENT, item) for item in element_ids)
        return Note(id, targets, text)
