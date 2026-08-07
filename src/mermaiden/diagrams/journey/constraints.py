from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import JourneySection, JourneyTask


class JourneyConstraint(Constraint, ABC):
    pass

@injectable(as_type=JourneyConstraint, qualifier="journey_structure")
class JourneyStructure(JourneyConstraint):
    @property
    def code(self) -> str:
        return "journey.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()

@injectable(as_type=JourneyConstraint, qualifier="journey_members")
class JourneyMembers(DiagramMembersConstraint, JourneyConstraint):
    element_types: ClassVar = (JourneySection, JourneyTask)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a user journey"
    relation_description: ClassVar[str] = "valid in a user journey"
    annotation_description: ClassVar[str] = "valid in a user journey"

    @property
    def code(self) -> str:
        return "journey.member_type"
