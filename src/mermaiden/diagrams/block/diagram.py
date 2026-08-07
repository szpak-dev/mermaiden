from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import BlockDiagramConfiguration
from .constraints import BlockAnnotationMember, BlockDiagramConstraint, BlockRelationMember
from .elements import BlockElementMember, BlockGroup, BlockNode, BlockSpace


@injectable(as_type=DiagramModel, qualifier="block", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class BlockDiagram(DiagramModel):
    constraints: Sequence[BlockDiagramConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "block.member_type",
        BlockElementMember,
        BlockRelationMember,
        BlockAnnotationMember,
    )
    configuration: BlockDiagramConfiguration = field(default_factory=BlockDiagramConfiguration, init=False)
    columns: int | None = field(default=None, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "block",
        "Block diagram",
        "block",
        "BlockDiagramConfig",
    )


    def set_columns(self, columns: int) -> None:
        object.__setattr__(self, "columns", columns)

    def add_group(self, id: str, label: str, columns: int | None = None, span: int | None = None) -> ChangeReport:
        return self._add_element(f"add group '{id}'", BlockGroup(id, label, (), columns, span))

    def add_block(self, id: str, label: str, span: int | None = None, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add block '{id}'", BlockNode(id, label, span), parent_id)

    def add_space(self, id: str, span: int | None = None, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add space '{id}'", BlockSpace(id, "space", span), parent_id)
