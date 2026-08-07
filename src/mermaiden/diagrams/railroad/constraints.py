from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import Alternative, Group, NonTerminal, Optional, Repetition, Sequence, Special, Terminal


class RailroadDiagramConstraint(Constraint, ABC):
    pass

@injectable(as_type=RailroadDiagramConstraint, qualifier="railroad_members")
class RailroadDiagramMembers(DiagramMembersConstraint, RailroadDiagramConstraint):
    element_types: ClassVar = (Terminal, NonTerminal, Special, Sequence, Alternative, Optional, Repetition, Group)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Railroad diagram"
    relation_description: ClassVar[str] = "valid in Railroad diagram"
    annotation_description: ClassVar[str] = "valid in Railroad diagram"

    @property
    def code(self) -> str:
        return "railroad.member_type"

@injectable(as_type=RailroadDiagramConstraint, qualifier="railroad_structure")
class RailroadDiagramStructure(RailroadDiagramConstraint):
    @property
    def code(self) -> str:
        return "railroad.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Railroad expression '{item.id}' must contain at least one term.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if isinstance(item, (Sequence, Alternative, Optional, Repetition, Group)) and not item.elements
        )
