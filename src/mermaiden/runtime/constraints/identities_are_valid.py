from collections import Counter

from wireup import injectable

from ...core.domain import Constraint, ConstraintDiagram, Violation
from ..domain import StructureConstraint


@injectable(as_type=Constraint, qualifier="identities_are_valid")
class IdentitiesAreValid(StructureConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        groups = (
            ("element", tuple(item.id for item in diagram.walk_elements())),
            ("relation", tuple(item.id for item in diagram.find_relations())),
            ("annotation", tuple(item.id for item in diagram.find_annotations())),
        )
        issues: list[Violation] = []
        for kind, identities in groups:
            issues.extend(
                self.violation(
                    f"{kind.title()} ID must not be blank.",
                    path=f"{kind}s",
                )
                for identity in identities
                if not identity.strip()
            )
            issues.extend(
                self.violation(
                    f"{kind.title()} '{identity}' already exists.",
                    path=f"{kind}s.{identity}",
                )
                for identity, count in Counter(identities).items()
                if count > 1
            )
        return tuple(issues)
