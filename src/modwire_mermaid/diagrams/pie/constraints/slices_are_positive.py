from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..elements import PieSlice
from .constraint import PieConstraint


@injectable(as_type=PieConstraint, qualifier="pie_slice_values")
class SlicesArePositive(PieConstraint):
    @property
    def code(self) -> str:
        return "pie.positive_slice"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(f"Pie slice '{slice.id}' must be greater than zero.", path=f"elements.{slice.id}")
            for slice in diagram.walk_elements()
            if isinstance(slice, PieSlice) and slice.value <= 0
        )
