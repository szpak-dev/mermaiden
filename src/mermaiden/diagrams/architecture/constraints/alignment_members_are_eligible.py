from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from .structure import ArchitectureConstraint


@injectable(as_type=ArchitectureConstraint, qualifier="architecture_alignment_members_are_eligible")
class AlignmentMembersAreEligible(ArchitectureConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        ineligible_ids = {
            element.id for element in diagram.walk_elements("") if element.kind not in ("service", "junction")
        }
        return tuple(
            self.violation(
                f"Alignment '{relation.id}' member '{member_id}' must be a service or junction.",
                path=f"relations.{relation.id}.element_ids",
            )
            for relation in diagram.find_relations("")
            if relation.kind == "alignment"
            for member_id in relation.element_ids
            if member_id in ineligible_ids
        )
