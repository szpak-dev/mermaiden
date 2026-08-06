from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, Violation
from ...core.diagram import Diagram


@injectable(as_type=Constraint, qualifier="relations_have_participants")
@dataclass(frozen=True, slots=True)
class RelationsHaveParticipants(Constraint):
    @property
    def code(self) -> str:
        return "structure.relation_participants"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Relation '{item.id}' has no participants.",
                path=f"relations.{item.id}",
            )
            for item in diagram.relations
            if not item.participant_ids
        )
