from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from .constraint import GanttConstraint


@injectable(as_type=GanttConstraint, qualifier="gantt_structure")
class GanttStructure(GanttConstraint):
    @property
    def code(self) -> str:
        return "gantt.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
