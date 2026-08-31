from collections.abc import Mapping, Sequence

from ...core.domain import Annotation, OperationError, TargetKind, TargetRef


class Note(Annotation):
    text: str


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
        targets = tuple(TargetRef(kind=TargetKind.ELEMENT, id=item) for item in element_ids)
        return Note(id=id, targets=targets, text=text)
