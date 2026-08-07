from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from .constraint import C4ContextDiagramConstraint


@injectable(as_type=C4ContextDiagramConstraint, qualifier="c4_structure")
class C4ContextDiagramStructure(C4ContextDiagramConstraint):
    @property
    def code(self) -> str:
        return "c4.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
