from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from .domain import TreeViewConstraint


@injectable(as_type=TreeViewConstraint, qualifier="treeview_acyclic")
class BranchesAreAcyclic(TreeViewConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        children: dict[str, list[str]] = {}
        for branch in self.branches(diagram):
            if len(branch.element_ids) == 2:
                children.setdefault(branch.parent_id, []).append(branch.child_id)

        visited: set[str] = set()
        active: set[str] = set()
        for item in diagram.walk_elements():
            if item.id in visited:
                continue
            stack: list[tuple[str, bool]] = [(item.id, False)]
            while stack:
                node, leaving = stack.pop()
                if leaving:
                    active.remove(node)
                    visited.add(node)
                    continue
                if node in active:
                    return (self.violation("Tree branches must not form a cycle.", path="relations"),)
                if node in visited:
                    continue
                active.add(node)
                stack.append((node, True))
                stack.extend((child, False) for child in reversed(children.get(node, [])))
        return ()
