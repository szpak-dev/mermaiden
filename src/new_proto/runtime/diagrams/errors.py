from dataclasses import dataclass

from ...core.constraint import ValidationReport


class DiagramBuildError(ValueError):
    pass


class DuplicateIdError(DiagramBuildError):
    pass


@dataclass(frozen=True, slots=True)
class DiagramValidationError(DiagramBuildError):
    report: ValidationReport

    def __str__(self) -> str:
        details = "; ".join(f"{item.code}: {item.message}" for item in self.report.violations)
        return details or "Diagram validation failed."
