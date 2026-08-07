

from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation


class ArchitectureConstraint(BlockingConstraint):
    pass


@injectable(as_type=ArchitectureConstraint, qualifier="architecture_structure")
class ArchitectureStructure(ArchitectureConstraint):
    @property
    def code(self) -> str:
        return "architecture.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
