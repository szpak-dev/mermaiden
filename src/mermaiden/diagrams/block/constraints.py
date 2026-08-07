from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import BlockGroup, BlockNode, BlockSpace


class BlockDiagramConstraint(Constraint, ABC):
    pass

@injectable(as_type=BlockDiagramConstraint, qualifier="block_members")
class BlockDiagramMembers(DiagramMembersConstraint, BlockDiagramConstraint):
    element_types: ClassVar = (BlockGroup, BlockNode, BlockSpace)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a block diagram"
    relation_description: ClassVar[str] = "valid in a block diagram"
    annotation_description: ClassVar[str] = "valid in a block diagram"

    @property
    def code(self) -> str:
        return "block.member_type"

@injectable(as_type=BlockDiagramConstraint, qualifier="block_structure")
class BlockDiagramStructure(BlockDiagramConstraint):
    @property
    def code(self) -> str:
        return "block.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
