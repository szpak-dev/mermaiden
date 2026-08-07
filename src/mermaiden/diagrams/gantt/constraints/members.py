from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import Marker, Milestone, Section, Task
from .constraint import GanttConstraint


@injectable(as_type=GanttConstraint, qualifier="gantt_members")
class GanttMembers(DiagramMembersConstraint, GanttConstraint):
    element_types: ClassVar = (Marker, Milestone, Section, Task)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a Gantt chart"
    relation_description: ClassVar[str] = "valid in a Gantt chart"
    annotation_description: ClassVar[str] = "valid in a Gantt chart"

    @property
    def code(self) -> str:
        return "gantt.member_type"
