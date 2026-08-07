from wireup import injectable

from ....core.annotation import TargetKind
from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..annotations import TreeAnnotation
from .constraint import TreeViewConstraint


@injectable(as_type=TreeViewConstraint, qualifier="treeview_annotations")
class AnnotationsAreValid(TreeViewConstraint):
    @property
    def code(self) -> str:
        return "treeview.annotations"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

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
