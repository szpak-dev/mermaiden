

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation


class ArchitectureConstraint(Constraint):
    pass


@injectable(as_type=ArchitectureConstraint, qualifier="architecture_structure")
class ArchitectureStructure(ArchitectureConstraint):
    @property
    def code(self) -> str:
        return "architecture.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
