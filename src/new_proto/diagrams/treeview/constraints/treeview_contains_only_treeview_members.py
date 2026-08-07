from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import Violation
from ....core.diagram import Diagram
from ..annotations import TreeAnnotation
from ..elements import TreeItem
from ..relations import TreeBranch
from .constraint import TreeViewConstraint


@injectable(as_type=TreeViewConstraint, qualifier="treeview_members")
@dataclass(frozen=True, slots=True)
class TreeViewContainsOnlyTreeViewMembers(TreeViewConstraint):
    @property
    def code(self) -> str:
        return "treeview.members"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        issues: list[Violation] = []
        issues.extend(
            self.violation(f"Element '{item.id}' is not valid in a Tree View.", path=f"elements.{item.id}")
            for item in diagram.walk_elements()
            if not isinstance(item, TreeItem)
        )
        issues.extend(
            self.violation(f"Relation '{item.id}' is not a tree branch.", path=f"relations.{item.id}")
            for item in diagram.find_relations()
            if not isinstance(item, TreeBranch)
        )
        issues.extend(
            self.violation(f"Annotation '{item.id}' is not valid in a Tree View.", path=f"annotations.{item.id}")
            for item in diagram.find_annotations()
            if not isinstance(item, TreeAnnotation)
        )
        return tuple(issues)
