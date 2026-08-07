

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation


class SequenceConstraint(Constraint):
    pass


@injectable(as_type=SequenceConstraint, qualifier="sequence_structure")
class SequenceStructure(SequenceConstraint):
    @property
    def code(self) -> str:
        return "sequence.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
