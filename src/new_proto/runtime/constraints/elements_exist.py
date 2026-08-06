from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, Violation
from ...core.diagram import Diagram


@injectable(as_type=Constraint, qualifier="elements_exist")
@dataclass(frozen=True, slots=True)
class ElementsExist(Constraint):
    @property
    def code(self) -> str:
        return "structure.elements_exist"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        if diagram.walk_elements():
            return ()
        return (self.violation("Diagram requires at least one element.", path="elements"),)
