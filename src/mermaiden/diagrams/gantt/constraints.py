from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)


class GanttConstraint(Constraint, ABC):
    pass

class GanttRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in a Gantt chart"


class GanttAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a Gantt chart"


@injectable(as_type=GanttConstraint, qualifier="gantt_structure")
class GanttStructure(GanttConstraint):
    @property
    def code(self) -> str:
        return "gantt.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
