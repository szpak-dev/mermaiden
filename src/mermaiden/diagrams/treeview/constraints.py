from wireup import injectable

from ...core.annotation import TargetKind
from ...core.constraint import ConstraintDiagram, Violation
from ..domain import DiagramConstraint
from .annotations import TreeAnnotation
from .elements import TreeItem
from .relations import TreeBranch


class TreeViewConstraint(DiagramConstraint):
    @staticmethod
    def branches(diagram: ConstraintDiagram) -> tuple[TreeBranch, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, TreeBranch))


@injectable(as_type=TreeViewConstraint, qualifier="treeview_annotations")
class AnnotationsAreValid(TreeViewConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues: list[Violation] = []
        for annotation in diagram.find_annotations():
            if not isinstance(annotation, TreeAnnotation):
                continue
            if len(annotation.targets) != 1 or annotation.targets[0].kind is not TargetKind.ELEMENT:
                issues.append(
                    self.violation(
                        f"Annotation '{annotation.id}' targets exactly one tree item.",
                        path=f"annotations.{annotation.id}",
                    )
                )
            if not annotation.highlight and not annotation.icon and not annotation.description:
                issues.append(
                    self.violation(
                        f"Annotation '{annotation.id}' must add a Tree View suffix.",
                        path=f"annotations.{annotation.id}",
                    )
                )
        return tuple(issues)


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


@injectable(as_type=TreeViewConstraint, qualifier="treeview_branches")
class BranchesAreValid(TreeViewConstraint):
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
