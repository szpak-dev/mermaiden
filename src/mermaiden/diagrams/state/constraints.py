from wireup import injectable

from ...core.annotation import TargetKind
from ...core.constraint import ConstraintDiagram, Violation
from ..domain import DiagramConstraint
from .annotations import StateNote
from .elements import StateEndpoint, StateNode
from .relations import StateTransition


class StateDiagramConstraint(DiagramConstraint):
    @staticmethod
    def transitions(diagram: ConstraintDiagram) -> tuple[StateTransition, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, StateTransition))


@injectable(as_type=StateDiagramConstraint, qualifier="state_notes")
class NotesAreValid(StateDiagramConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements()}
        return tuple(
            self.violation(f"Note '{note.id}' must target one state node.", path=f"annotations.{note.id}")
            for note in diagram.find_annotations()
            if isinstance(note, StateNote)
            if len(note.targets) != 1
            or note.targets[0].kind is not TargetKind.ELEMENT
            or not isinstance(elements.get(note.targets[0].id), StateNode)
        )


@injectable(as_type=StateDiagramConstraint, qualifier="state_transitions")
class TransitionsAreValid(StateDiagramConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements()}
        issues: list[Violation] = []
        for transition in self.transitions(diagram):
            if len(transition.element_ids) != 2:
                issues.append(
                    self.violation(
                        f"Transition '{transition.id}' requires exactly one source and one target.",
                        path=f"relations.{transition.id}",
                    )
                )
                continue
            for endpoint in (transition.source_id, transition.target_id):
                if not isinstance(elements.get(endpoint), StateEndpoint):
                    issues.append(
                        self.violation(
                            f"Transition '{transition.id}' endpoint '{endpoint}' must be a state node.",
                            path=f"relations.{transition.id}",
                        )
                    )
        return tuple(issues)
