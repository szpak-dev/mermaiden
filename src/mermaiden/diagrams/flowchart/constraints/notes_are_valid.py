from wireup import injectable

from ....core.domain import ConstraintDiagram, TargetKind, Violation
from ..annotations import Note
from .domain import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="notes_are_valid")
class NotesAreValid(FlowchartConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues: list[Violation] = []
        for note in (item for item in diagram.find_annotations() if isinstance(item, Note)):
            if not note.text.strip():
                issues.append(
                    self.violation(
                        f"Note '{note.id}' requires text.",
                        path=f"annotations.{note.id}",
                    )
                )
            if any(target.kind is not TargetKind.ELEMENT for target in note.targets):
                issues.append(
                    self.violation(
                        f"Note '{note.id}' can only target elements.",
                        path=f"annotations.{note.id}",
                    )
                )
        return tuple(issues)
