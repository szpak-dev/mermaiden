from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ConstraintLevel, Violation
from ...core.diagram import Diagram
from .annotations import ArchitectureNote
from .elements import ArchitectureGroup, Junction, Service
from .relations import Edge


class ArchitectureConstraint(Constraint):
    pass


@injectable(as_type=ArchitectureConstraint, qualifier="architecture_members")
@dataclass(frozen=True, slots=True)
class ArchitectureMembers(ArchitectureConstraint):
    @property
    def code(self) -> str:
        return "architecture.members"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        valid = ArchitectureGroup | Service | Junction
        issues = [
            self.violation(f"Element '{item.id}' is not an architecture member.")
            for item in diagram.walk_elements()
            if not isinstance(item, valid)
        ]
        issues.extend(
            self.violation(f"Relation '{item.id}' is not an architecture edge.")
            for item in diagram.find_relations()
            if not isinstance(item, Edge)
        )
        issues.extend(
            self.violation(f"Annotation '{item.id}' is not an architecture note.")
            for item in diagram.find_annotations()
            if not isinstance(item, ArchitectureNote)
        )
        return tuple(issues)
