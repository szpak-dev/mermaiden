from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..elements import PieSlice
from .constraint import PieConstraint


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
