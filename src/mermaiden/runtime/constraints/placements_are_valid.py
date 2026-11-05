from wireup import injectable

from ...core.domain import Constraint, ConstraintDiagram, Container, Element, Violation
from ..domain import StructureConstraint


@injectable(as_type=Constraint, qualifier="placements_are_valid")
class PlacementsAreValid(StructureConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        pending: list[tuple[Element, type[Container] | None]] = [(element, None) for element in diagram.root_elements]
        issues: list[Violation] = []
        while pending:
            element, parent_type = pending.pop()
            if not diagram.accepts_parent(type(element), parent_type):
                destination = "$root" if parent_type is None else parent_type.__name__
                issues.append(
                    self.violation(
                        f"Element '{element.id}' of kind '{element.kind}' cannot be placed in {destination}.",
                        path=f"elements.{element.id}",
                    )
                )
            pending.extend(element.child_placements)
        return tuple(issues)
