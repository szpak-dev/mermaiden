
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation


class JourneyConstraint(BlockingConstraint):
    pass



@injectable(as_type=JourneyConstraint, qualifier="journey_structure")
class JourneyStructure(JourneyConstraint):
    @property
    def code(self) -> str:
        return "journey.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
