from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)
from .elements import Alternative, Group, Optional, Repetition, Sequence


class RailroadDiagramConstraint(Constraint, ABC):
    pass

class RailroadRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in Railroad diagram"


class RailroadAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in Railroad diagram"


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
