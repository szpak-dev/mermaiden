from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .annotation import Annotation
from .element import Element
from .relation import Relation


class ConstraintLevel(StrEnum):
    BLOCKING = "blocking"
    ADVISORY = "advisory"


class ConstraintDiagram(Protocol):
    def walk_elements(self, parent_id: str = "") -> Sequence[Element]: ...

    def find_relations(self, element_id: str = "") -> Sequence[Relation]: ...

    def find_annotations(self, target_id: str = "") -> Sequence[Annotation]: ...


@dataclass(frozen=True, slots=True)
class Violation:
    code: str
    message: str
    path: str = ""
    level: ConstraintLevel = ConstraintLevel.ADVISORY


@dataclass(frozen=True, slots=True)
class ValidationReport:
    violations: tuple[Violation, ...] = ()

    @property
    def blocking(self) -> tuple[Violation, ...]:
        return tuple(item for item in self.violations if item.level is ConstraintLevel.BLOCKING)

    @property
    def advisory(self) -> tuple[Violation, ...]:
        return tuple(item for item in self.violations if item.level is ConstraintLevel.ADVISORY)

    @property
    def can_commit(self) -> bool:
        return not self.blocking

    @property
    def is_valid(self) -> bool:
        return not self.violations

    def __bool__(self) -> bool:
        return self.can_commit


@dataclass(frozen=True, slots=True)
class ChangeReport:
    operation: str
    before: ValidationReport
    after: ValidationReport
    accepted: bool

    @property
    def introduced(self) -> tuple[Violation, ...]:
        return tuple(item for item in self.after.violations if item not in self.before.violations)

    @property
    def resolved(self) -> tuple[Violation, ...]:
        return tuple(item for item in self.before.violations if item not in self.after.violations)

    @property
    def current(self) -> ValidationReport:
        return self.after if self.accepted else self.before


@dataclass(frozen=True, slots=True)
class ChangeRejected(RuntimeError):
    operation: str
    report: ValidationReport

    def __str__(self) -> str:
        details = "; ".join(item.message for item in self.report.blocking)
        return f"Cannot {self.operation}: {details or 'the operation was rejected.'}"


class Constraint(ABC):
    @property
    @abstractmethod
    def code(self) -> str: ...

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.ADVISORY

    @abstractmethod
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]: ...

    def violation(self, message: str, *, path: str = "") -> Violation:
        return Violation(code=self.code, message=message, path=path, level=self.level)


class BlockingConstraint(Constraint):
    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING
