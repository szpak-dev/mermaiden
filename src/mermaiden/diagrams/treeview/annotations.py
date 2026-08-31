from collections.abc import Mapping, Sequence

from ...core.domain import Annotation, OperationError, TargetKind, TargetRef


class TreeAnnotation(Annotation):
    highlight: bool = False
    icon: str = ""
    description: str = ""


class TreeAnnotations:
    def create(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str],
        relation_ids: Sequence[str],
    ) -> TreeAnnotation:
        if relation_ids or len(element_ids) != 1:
            raise OperationError("Tree View annotations target exactly one element.")
        allowed = {"highlight", "icon", "description"}
        if not data or not set(data).issubset(allowed):
            raise OperationError("Tree View annotations use highlight, icon, and/or description.")
        highlight = data.get("highlight", False)
        icon = data.get("icon", "")
        description = data.get("description", "")
        if not isinstance(highlight, bool) or not isinstance(icon, str) or not isinstance(description, str):
            raise OperationError("Tree View annotation values must be bool or strings.")
        if "\n" in description or "\r" in description:
            raise OperationError("Tree View descriptions must be one line.")
        return TreeAnnotation(
            id=id,
            targets=(TargetRef(kind=TargetKind.ELEMENT, id=element_ids[0]),),
            highlight=highlight,
            icon=icon,
            description=description,
        )
