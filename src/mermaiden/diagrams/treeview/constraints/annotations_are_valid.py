from wireup import injectable

from ....core.domain import ConstraintDiagram, TargetKind, Violation
from ..annotations import TreeAnnotation
from .domain import TreeViewConstraint


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
