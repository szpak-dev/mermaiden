from wireup import injectable

from ...core.constraint import BlockingConstraint, Constraint, ConstraintDiagram, Violation


@injectable(as_type=Constraint, qualifier="labels_are_present")
class LabelsArePresent(BlockingConstraint):
    @property
    def code(self) -> str:
        return "structure.labels"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Element '{item.id}' requires a label.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if not item.label.strip()
        )
