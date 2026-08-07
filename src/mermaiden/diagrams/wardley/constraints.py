from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import (
    DiagramAnnotationMember,
)
from .elements import Component, Evolution


class WardleyDiagramConstraint(Constraint, ABC):
    pass

class WardleyAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in Wardley map"


@injectable(as_type=WardleyDiagramConstraint, qualifier="wardley_structure")
class WardleyDiagramStructure(WardleyDiagramConstraint):
    @property
    def code(self) -> str:
        return "wardley.structure"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        components = {item.id for item in diagram.walk_elements() if isinstance(item, Component)}
        issues = [
            self.violation(
                f"Wardley component '{item.id}' coordinates must be between 0 and 1.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if isinstance(item, Component) and not (0 <= item.visibility <= 1 and 0 <= item.evolution <= 1)
        ]
        issues.extend(
            self.violation(
                f"Wardley evolution '{item.id}' references an unknown component.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if isinstance(item, Evolution) and item.label not in components
        )
        return tuple(issues)
