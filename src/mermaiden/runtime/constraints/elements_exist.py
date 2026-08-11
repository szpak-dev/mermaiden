from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import StructureConstraint


@injectable(as_type=Constraint, qualifier="elements_exist")
class ElementsExist(StructureConstraint):

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        if diagram.walk_elements():
            return ()
        return (self.violation("Diagram requires at least one element.", path="elements"),)
