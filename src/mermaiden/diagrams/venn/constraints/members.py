from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import VennSet, VennText, VennUnion
from .constraint import VennConstraint


@injectable(as_type=VennConstraint, qualifier="venn_members")
class VennMembers(DiagramMembersConstraint, VennConstraint):
    element_types: ClassVar = (VennSet, VennText, VennUnion)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a Venn diagram"
    relation_description: ClassVar[str] = "valid in a Venn diagram"
    annotation_description: ClassVar[str] = "valid in a Venn diagram"

    @property
    def code(self) -> str:
        return "venn.member_type"
