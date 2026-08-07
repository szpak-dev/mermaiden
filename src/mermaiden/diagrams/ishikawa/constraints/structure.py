from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from ..elements import Category, Cause, Effect
from .constraint import IshikawaDiagramConstraint


@injectable(as_type=IshikawaDiagramConstraint, qualifier="ishikawa_structure")
class IshikawaDiagramStructure(IshikawaDiagramConstraint):
    @property
    def code(self) -> str:
        return "ishikawa.structure"

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
