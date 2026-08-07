from wireup import injectable

from ...core.constraint import BlockingConstraint, Constraint, ConstraintDiagram, Violation


@injectable(as_type=Constraint, qualifier="annotations_have_targets")
class AnnotationsHaveTargets(BlockingConstraint):
    @property
    def code(self) -> str:
        return "structure.annotation_targets"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Annotation '{item.id}' requires at least one target.",
                path=f"annotations.{item.id}",
            )
            for item in diagram.find_annotations()
            if not item.targets
        )
