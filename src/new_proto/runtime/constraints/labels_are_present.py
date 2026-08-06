from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ConstraintLevel, Violation
from ...core.diagram import Diagram


@injectable(as_type=Constraint, qualifier="labels_are_present")
@dataclass(frozen=True, slots=True)
class LabelsArePresent(Constraint):
    @property
    def code(self) -> str:
        return "structure.labels"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(
                f"Element '{item.id}' requires a label.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if not item.label.strip()
        ]
        issues.extend(
            self.violation(
                f"Relation '{item.id}' requires a label.",
                path=f"relations.{item.id}",
            )
            for item in diagram.find_relations()
            if not item.label.strip()
        )
        return tuple(issues)
