from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation


@injectable(as_type=Constraint, qualifier="elements_exist")
class ElementsExist(Constraint):
    @property
    def code(self) -> str:
        return "structure.elements_exist"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        if diagram.walk_elements():
            return ()
        return (self.violation("Diagram requires at least one element.", path="elements"),)
