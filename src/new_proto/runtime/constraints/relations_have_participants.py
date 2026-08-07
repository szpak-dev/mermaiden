from wireup import injectable

from ...core.constraint import BlockingConstraint, Constraint, ConstraintDiagram, Violation


@injectable(as_type=Constraint, qualifier="relations_have_participants")
class RelationsHaveParticipants(BlockingConstraint):
    @property
    def code(self) -> str:
        return "structure.relation_participants"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Relation '{item.id}' requires at least two elements.",
                path=f"relations.{item.id}",
            )
            for item in diagram.find_relations()
            if len(item.element_ids) < 2
        )
