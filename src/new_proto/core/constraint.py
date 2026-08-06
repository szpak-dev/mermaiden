from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .diagram import Diagram


class ConstraintLevel(StrEnum):
    """Determines whether a violation prevents an atomic state change."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


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
    """Constraint delta produced by one attempted aggregate operation."""

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
    """A side-effect-free Visitor evaluating one rule against a Diagram."""

    @property
    @abstractmethod
    def code(self) -> str: ...

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.ADVISORY

    @abstractmethod
    def visit(self, diagram: "Diagram") -> tuple[Violation, ...]: ...

    def violation(self, message: str, *, path: str = "") -> Violation:
        return Violation(code=self.code, message=message, path=path, level=self.level)
