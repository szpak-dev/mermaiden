from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from .diagram import Diagram, DiagramVisitor


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class Violation:
    code: str
    message: str
    path: str = ""
    severity: Severity = Severity.ERROR


@dataclass(frozen=True, slots=True)
class ValidationReport:
    violations: tuple[Violation, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not any(item.severity is Severity.ERROR for item in self.violations)

    def __bool__(self) -> bool:
        return self.is_valid


class Constraint(DiagramVisitor[tuple[Violation, ...]], ABC):
    """A side-effect-free Visitor that checks one diagram policy."""

    @property
    @abstractmethod
    def code(self) -> str: ...

    @abstractmethod
    def visit(self, diagram: Diagram) -> tuple[Violation, ...]: ...

    def violation(self, message: str, *, path: str = "") -> Violation:
        return Violation(code=self.code, message=message, path=path)

