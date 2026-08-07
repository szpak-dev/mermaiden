from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import BlockGroup, BlockNode, BlockSpace
from .constraint import BlockDiagramConstraint


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
