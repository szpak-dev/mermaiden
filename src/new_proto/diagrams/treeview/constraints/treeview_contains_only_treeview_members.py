from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..annotations import TreeAnnotation
from ..elements import TreeItem
from ..relations import TreeBranch
from .constraint import TreeViewConstraint


@injectable(as_type=TreeViewConstraint, qualifier="treeview_members")
class TreeViewContainsOnlyTreeViewMembers(DiagramMembersConstraint, TreeViewConstraint):
    element_types: ClassVar = (TreeItem,)
    relation_types: ClassVar = (TreeBranch,)
    annotation_types: ClassVar = (TreeAnnotation,)
    element_description: ClassVar[str] = "valid in a Tree View"
    relation_description: ClassVar[str] = "a tree branch"
    annotation_description: ClassVar[str] = "valid in a Tree View"

    @property
    def code(self) -> str:
        return "treeview.members"
