from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import DiagramMembersConstraint
from .elements import PieSlice


class PieConstraint(Constraint, ABC):
    pass

@injectable(as_type=PieConstraint, qualifier="pie_members")
class PieContainsOnlyPieMembers(DiagramMembersConstraint, PieConstraint):
    element_types: ClassVar = (PieSlice,)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "a pie slice"
    relation_description: ClassVar[str] = "valid in a pie chart"
    annotation_description: ClassVar[str] = "valid in a pie chart"

    @property
    def code(self) -> str:
        return "pie.member_type"

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
