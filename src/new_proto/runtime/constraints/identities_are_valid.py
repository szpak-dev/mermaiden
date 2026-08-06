from collections import Counter
from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ConstraintLevel, Violation
from ...core.diagram import Diagram


@injectable(as_type=Constraint, qualifier="identities_are_valid")
@dataclass(frozen=True, slots=True)
class IdentitiesAreValid(Constraint):
    @property
    def code(self) -> str:
        return "structure.identities"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
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
