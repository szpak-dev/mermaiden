from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ConstraintLevel, Violation
from ...core.diagram import Diagram


@injectable(as_type=Constraint, qualifier="annotations_have_targets")
@dataclass(frozen=True, slots=True)
class AnnotationsHaveTargets(Constraint):
    @property
    def code(self) -> str:
        return "structure.annotation_targets"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Annotation '{item.id}' requires at least one target.",
                path=f"annotations.{item.id}",
            )
            for item in diagram.find_annotations()
            if not item.targets
        )
