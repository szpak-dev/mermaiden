from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)


class TimelineConstraint(Constraint, ABC):
    pass

class TimelineRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in a timeline"


class TimelineAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a timeline"


@injectable(as_type=TimelineConstraint, qualifier="timeline_structure")
class TimelineStructure(TimelineConstraint):
    @property
    def code(self) -> str:
        return "timeline.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
