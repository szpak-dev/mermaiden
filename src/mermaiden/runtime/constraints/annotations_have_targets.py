from wireup import injectable

from ...core.domain import Constraint, ConstraintDiagram, Violation
from ..domain import StructureConstraint


@injectable(as_type=Constraint, qualifier="annotations_have_targets")
class AnnotationsHaveTargets(StructureConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Annotation '{item.id}' requires at least one target.",
                path=f"annotations.{item.id}",
            )
            for item in diagram.find_annotations()
            if not item.targets
        )
