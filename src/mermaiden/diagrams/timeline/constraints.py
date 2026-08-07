
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation


class TimelineConstraint(BlockingConstraint):
    pass



@injectable(as_type=TimelineConstraint, qualifier="timeline_structure")
class TimelineStructure(TimelineConstraint):
    @property
    def code(self) -> str:
        return "timeline.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
