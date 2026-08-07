from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import (
    DiagramAnnotationMember,
)


class SankeyConstraint(Constraint):
    @property
    def code(self) -> str:
        return "sankey.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()

class SankeyAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a Sankey diagram"


@injectable(as_type=SankeyConstraint, qualifier="sankey_structure")
class SankeyStructure(SankeyConstraint):
    pass
