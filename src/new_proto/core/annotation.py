from collections.abc import Mapping
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
    """Typed non-structural data attached to elements or relations."""

    id: str
    targets: tuple[TargetRef, ...]


@dataclass(frozen=True, slots=True)
class DataAnnotation(Annotation):
    """Generic mapping-backed annotation used by the base diagram runtime."""

    data: Mapping[str, object]
