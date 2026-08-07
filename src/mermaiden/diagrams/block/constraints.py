from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)


class BlockDiagramConstraint(Constraint, ABC):
    pass

class BlockRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in a block diagram"


class BlockAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a block diagram"


@injectable(as_type=BlockDiagramConstraint, qualifier="block_structure")
class BlockDiagramStructure(BlockDiagramConstraint):
    @property
    def code(self) -> str:
        return "block.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
