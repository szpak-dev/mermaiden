from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)
from .elements import VennSet, VennUnion


class VennConstraint(Constraint, ABC):
    pass

class VennRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in a Venn diagram"


class VennAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a Venn diagram"


@injectable(as_type=VennConstraint, qualifier="venn_structure")
class VennStructure(VennConstraint):
    @property
    def code(self) -> str:
        return "venn.structure"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        known_sets = {item.id for item in diagram.walk_elements() if isinstance(item, VennSet)}
        return tuple(
            self.violation(
                f"Venn union '{item.id}' references undefined sets: {', '.join(missing)}.",
                path=f"elements.{item.id}",
            )
            for item in diagram.root_elements
            if isinstance(item, VennUnion)
            if (missing := tuple(set(item.set_ids).difference(known_sets)))
        )
