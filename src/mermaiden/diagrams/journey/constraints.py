from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)


class JourneyConstraint(Constraint, ABC):
    pass

class JourneyRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in a user journey"


class JourneyAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a user journey"


@injectable(as_type=JourneyConstraint, qualifier="journey_structure")
class JourneyStructure(JourneyConstraint):
    @property
    def code(self) -> str:
        return "journey.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
