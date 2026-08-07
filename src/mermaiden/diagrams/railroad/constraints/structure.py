from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from ..elements import Alternative, Group, Optional, Repetition, Sequence
from .constraint import RailroadDiagramConstraint


@injectable(as_type=RailroadDiagramConstraint, qualifier="railroad_structure")
class RailroadDiagramStructure(RailroadDiagramConstraint):
    @property
    def code(self) -> str:
        return "railroad.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Railroad expression '{item.id}' must contain at least one term.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if isinstance(item, (Sequence, Alternative, Optional, Repetition, Group)) and not item.elements
        )
