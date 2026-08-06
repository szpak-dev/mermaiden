from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class TargetKind(StrEnum):
    DIAGRAM = "diagram"
    ELEMENT = "element"
    RELATION = "relation"


@dataclass(frozen=True, slots=True)
class TargetRef:
    """Stable reference from an annotation to an annotatable diagram member."""

    kind: TargetKind
    id: str


class Annotation(ABC):
    """Optional metadata kept separate from structural diagram semantics."""

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def targets(self) -> tuple[TargetRef, ...]: ...

