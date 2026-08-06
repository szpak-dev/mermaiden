from dataclasses import dataclass
from enum import StrEnum


class TargetKind(StrEnum):
    ELEMENT = "element"
    RELATION = "relation"


@dataclass(frozen=True, slots=True)
class TargetRef:
    """Stable reference to an annotated diagram building block."""

    kind: TargetKind
    id: str


@dataclass(frozen=True, slots=True)
class Annotation:
    """Additional non-structural data attached to elements or relations."""

    id: str
    targets: tuple[TargetRef, ...]
    data: object | None = None
