from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import TimelineEvent, TimelinePeriod, TimelineSection


class TimelineConstraint(Constraint, ABC):
    pass

@injectable(as_type=TimelineConstraint, qualifier="timeline_structure")
class TimelineStructure(TimelineConstraint):
    @property
    def code(self) -> str:
        return "timeline.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()

@injectable(as_type=TimelineConstraint, qualifier="timeline_members")
class TimelineMembers(DiagramMembersConstraint, TimelineConstraint):
    element_types: ClassVar = (TimelineSection, TimelinePeriod, TimelineEvent)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a timeline"
    relation_description: ClassVar[str] = "valid in a timeline"
    annotation_description: ClassVar[str] = "valid in a timeline"

    @property
    def code(self) -> str:
        return "timeline.member_type"
