from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar

from ...core.annotation import Annotation, TargetKind, TargetRef
from ...core.error import OperationError


@dataclass(frozen=True, slots=True)
class TreeAnnotation(Annotation):
    kind: ClassVar[str] = "tree_annotation"
    highlight: bool = False
    icon: str = ""
    description: str = ""


@dataclass(frozen=True, slots=True)
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
        return TreeAnnotation(id, (TargetRef(TargetKind.ELEMENT, element_ids[0]),), highlight, icon, description)
