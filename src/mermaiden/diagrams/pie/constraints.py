
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation
from .elements import PieSlice


class PieConstraint(BlockingConstraint):
    pass



@injectable(as_type=PieConstraint, qualifier="pie_slice_values")
class SlicesArePositive(PieConstraint):
    @property
    def code(self) -> str:
        return "pie.positive_slice"


    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(f"Pie slice '{slice.id}' must be greater than zero.", path=f"elements.{slice.id}")
            for slice in diagram.walk_elements()
            if isinstance(slice, PieSlice) and slice.value <= 0
        )
