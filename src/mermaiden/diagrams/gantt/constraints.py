
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation


class GanttConstraint(BlockingConstraint):
    pass



@injectable(as_type=GanttConstraint, qualifier="gantt_structure")
class GanttStructure(GanttConstraint):
    @property
    def code(self) -> str:
        return "gantt.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
