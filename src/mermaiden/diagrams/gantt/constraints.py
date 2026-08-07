from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import Marker, Milestone, Section, Task


class GanttConstraint(Constraint, ABC):
    pass

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

@injectable(as_type=GanttConstraint, qualifier="gantt_structure")
class GanttStructure(GanttConstraint):
    @property
    def code(self) -> str:
        return "gantt.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
