from collections.abc import Mapping
from enum import StrEnum

from .model import ClassifiedValueModel, ValueModel


class TargetKind(StrEnum):
    ELEMENT = "element"
    RELATION = "relation"


class TargetRef(ValueModel):

    kind: TargetKind
    id: str


class Annotation(ClassifiedValueModel):

    id: str
    targets: tuple[TargetRef, ...]


class DataAnnotation(Annotation):
    data: Mapping[str, object]
