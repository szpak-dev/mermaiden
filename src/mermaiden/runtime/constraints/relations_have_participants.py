from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import StructureConstraint


@injectable(as_type=Constraint, qualifier="relations_have_participants")
class RelationsHaveParticipants(StructureConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Relation '{item.id}' requires at least two elements.",
                path=f"relations.{item.id}",
            )
            for item in diagram.find_relations()
            if len(item.element_ids) < 2
        )
