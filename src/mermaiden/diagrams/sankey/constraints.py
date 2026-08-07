from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import SankeyNode
from .relations import SankeyLink


class SankeyConstraint(Constraint):
    @property
    def code(self) -> str:
        return "sankey.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()

@injectable(as_type=SankeyConstraint, qualifier="sankey_structure")
class SankeyStructure(SankeyConstraint):
    pass

@injectable(as_type=SankeyConstraint, qualifier="sankey_members")
class SankeyMembers(DiagramMembersConstraint, SankeyConstraint):
    element_types: ClassVar = (SankeyNode,)
    relation_types: ClassVar = (SankeyLink,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "a Sankey node"
    relation_description: ClassVar[str] = "a Sankey link"
    annotation_description: ClassVar[str] = "valid in a Sankey diagram"

    @property
    def code(self) -> str:
        return "sankey.member_type"
