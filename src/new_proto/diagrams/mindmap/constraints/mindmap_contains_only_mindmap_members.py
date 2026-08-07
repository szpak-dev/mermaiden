from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..elements import MindmapNode
from .constraint import MindmapConstraint


@injectable(as_type=MindmapConstraint, qualifier="mindmap_members")
class MindmapContainsOnlyMindmapMembers(DiagramMembersConstraint, MindmapConstraint):
    element_types: ClassVar = (MindmapNode,)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "a mindmap node"
    relation_description: ClassVar[str] = "valid in a mindmap"
    annotation_description: ClassVar[str] = "valid in a mindmap"

    @property
    def code(self) -> str:
        return "mindmap.member_type"
