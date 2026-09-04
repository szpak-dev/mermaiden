from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..elements import TreeItem, TreeItemType
from .domain import TreeViewConstraint


@injectable(as_type=TreeViewConstraint, qualifier="treeview_files_are_leaves")
class FilesAreLeaves(TreeViewConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements("")}
        return tuple(
            self.violation(
                f"File '{branch.parent_id}' cannot be the parent of a tree branch.",
                path=f"relations.{branch.id}",
            )
            for branch in self.branches(diagram)
            if isinstance(parent := elements.get(branch.parent_id), TreeItem) and parent.item_type is TreeItemType.FILE
        )
