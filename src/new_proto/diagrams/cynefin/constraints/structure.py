from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from .constraint import CynefinDiagramConstraint


@injectable(as_type=CynefinDiagramConstraint, qualifier="cynefin_structure")
class CynefinDiagramStructure(CynefinDiagramConstraint):
    @property
    def code(self) -> str:
        return "cynefin.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
