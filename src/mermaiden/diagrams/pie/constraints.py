from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)
from .elements import PieSlice


class PieConstraint(Constraint, ABC):
    pass

class PieRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in a pie chart"


class PieAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a pie chart"


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
