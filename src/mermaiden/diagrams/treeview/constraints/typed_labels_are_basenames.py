from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..elements import TreeItem, TreeItemType
from .domain import TreeViewConstraint


@injectable(as_type=TreeViewConstraint, qualifier="treeview_typed_labels_are_basenames")
class TypedLabelsAreBasenames(TreeViewConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"{item.item_type.value.capitalize()} '{item.id}' label must be a basename without path separators.",
                path=f"elements.{item.id}.label",
            )
            for item in diagram.walk_elements("")
            if isinstance(item, TreeItem)
            and item.item_type is not TreeItemType.ITEM
            and ("/" in item.label or "\\" in item.label)
        )
