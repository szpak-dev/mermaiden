from wireup import injectable

from ...core.domain import ConstraintDiagram, Violation
from ..domain import DiagramConstraint
from .elements import Category, Cause, Effect


class IshikawaDiagramConstraint(DiagramConstraint):
    pass


@injectable(as_type=IshikawaDiagramConstraint, qualifier="ishikawa_structure")
class IshikawaDiagramStructure(IshikawaDiagramConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        effects = tuple(item for item in diagram.root_elements if isinstance(item, Effect))
        issues = [
            self.violation("Ishikawa diagrams should define exactly one effect.", path="elements")
            for _ in [None]
            if len(effects) != 1
        ]
        issues.extend(
            self.violation(f"Ishikawa cause '{item.id}' should belong to a category.", path=f"elements.{item.id}")
            for item in diagram.root_elements
            if isinstance(item, Cause)
        )
        issues.extend(
            self.violation(f"Ishikawa category '{item.id}' must have a label.", path=f"elements.{item.id}")
            for item in diagram.root_elements
            if isinstance(item, Category) and not item.label
        )
        return tuple(issues)
