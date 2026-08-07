from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


class TargetKind(StrEnum):
    ELEMENT = "element"
    RELATION = "relation"


@dataclass(frozen=True, slots=True)
class TargetRef:
    kind: TargetKind
    id: str


@dataclass(frozen=True, slots=True)
class Annotation:
    id: str
    targets: tuple[TargetRef, ...]


@dataclass(frozen=True, slots=True)
class DataAnnotation(Annotation):
    data: Mapping[str, object]
