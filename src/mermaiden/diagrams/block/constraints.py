
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation


class BlockDiagramConstraint(BlockingConstraint):
    pass



@injectable(as_type=BlockDiagramConstraint, qualifier="block_structure")
class BlockDiagramStructure(BlockDiagramConstraint):
    @property
    def code(self) -> str:
        return "block.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
