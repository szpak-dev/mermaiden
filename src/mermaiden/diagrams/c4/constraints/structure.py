from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..elements import C4Element
from ..relations import Relationship
from .constraint import C4ContextDiagramConstraint


@injectable(as_type=C4ContextDiagramConstraint, qualifier="c4_structure")
class C4ContextDiagramStructure(C4ContextDiagramConstraint):
    @property
    def code(self) -> str:
        return "c4.structure"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(f"C4 element '{item.id}' must use a Mermaid-safe identifier.", path=f"elements.{item.id}")
            for item in diagram.walk_elements()
            if isinstance(item, C4Element) and (not item.id or not item.id.replace("_", "").isalnum())
        ]
        issues.extend(
            self.violation(f"C4 element '{item.id}' must have a label.", path=f"elements.{item.id}")
            for item in diagram.walk_elements()
            if isinstance(item, C4Element) and not item.label
        )
        issues.extend(
            self.violation(
                f"C4 relationship '{item.id}' cannot reference the same element twice.",
                path=f"relations.{item.id}",
            )
            for item in diagram.find_relations()
            if isinstance(item, Relationship)
            if len(item.element_ids) == 2 and item.element_ids[0] == item.element_ids[1]
        )
        return tuple(issues)
