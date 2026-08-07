from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..elements import TreeItem
from .constraint import TreeViewConstraint


@injectable(as_type=TreeViewConstraint, qualifier="treeview_branches")
class BranchesAreValid(TreeViewConstraint):
    @property
    def code(self) -> str:
        return "treeview.branches"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements()}
        parents: set[str] = set()
        issues: list[Violation] = []
        for branch in self.branches(diagram):
            if len(branch.element_ids) != 2:
                issues.append(
                    self.violation(
                        f"Branch '{branch.id}' needs one parent and one child.",
                        path=f"relations.{branch.id}",
                    )
                )
                continue
            parent_id, child_id = branch.element_ids
            if parent_id == child_id:
                issues.append(
                    self.violation(f"Branch '{branch.id}' cannot point to itself.", path=f"relations.{branch.id}")
                )
            if not isinstance(elements.get(parent_id), TreeItem) or not isinstance(elements.get(child_id), TreeItem):
                issues.append(
                    self.violation(f"Branch '{branch.id}' endpoints must be tree items.", path=f"relations.{branch.id}")
                )
            if child_id in parents:
                issues.append(
                    self.violation(f"Tree item '{child_id}' has more than one parent.", path=f"relations.{branch.id}")
                )
            parents.add(child_id)
        return tuple(issues)
