from collections.abc import Mapping, Sequence

from ...core.annotation import Annotation, TargetKind, TargetRef
from ...core.error import OperationError


class ClassNote(Annotation):
    text: str


class ClassNotes:
    def create(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str],
        relation_ids: Sequence[str],
    ) -> ClassNote:
        if relation_ids or len(element_ids) != 1:
            raise OperationError("Class notes target exactly one class.")
        if set(data) != {"text"} or not isinstance(data.get("text"), str):
            raise OperationError("Class notes require exactly one string 'text' value.")
        text = data["text"]
        assert isinstance(text, str)
        return ClassNote(id, (TargetRef(TargetKind.ELEMENT, element_ids[0]),), text)
