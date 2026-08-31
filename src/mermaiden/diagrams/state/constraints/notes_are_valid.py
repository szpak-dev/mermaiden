from wireup import injectable

from ....core.domain import ConstraintDiagram, TargetKind, Violation
from ..annotations import StateNote
from ..elements import StateNode
from .domain import StateDiagramConstraint


@injectable(as_type=StateDiagramConstraint, qualifier="state_notes")
class NotesAreValid(StateDiagramConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements("")}
        return tuple(
            self.violation(f"Note '{note.id}' must target one state node.", path=f"annotations.{note.id}")
            for note in diagram.find_annotations("")
            if isinstance(note, StateNote)
            if len(note.targets) != 1
            or note.targets[0].kind is not TargetKind.ELEMENT
            or not isinstance(elements.get(note.targets[0].id), StateNode)
        )
