
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation


class SankeyConstraint(BlockingConstraint):
    @property
    def code(self) -> str:
        return "sankey.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()


@injectable(as_type=SankeyConstraint, qualifier="sankey_structure")
class SankeyStructure(SankeyConstraint):
    pass
