
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation
from .elements import Column, Task


class KanbanDiagramConstraint(BlockingConstraint):
    pass



@injectable(as_type=KanbanDiagramConstraint, qualifier="kanban_structure")
class KanbanDiagramStructure(KanbanDiagramConstraint):
    @property
    def code(self) -> str:
        return "kanban.structure"


    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        priorities = {"Very High", "High", "Low", "Very Low"}
        issues = [
            self.violation(f"Kanban column '{item.id}' must have a label.", path=f"elements.{item.id}")
            for item in diagram.root_elements
            if isinstance(item, Column) and not item.label
        ]
        issues.extend(
            self.violation(f"Kanban task '{item.id}' must belong to a column.", path=f"elements.{item.id}")
            for item in diagram.root_elements
            if isinstance(item, Task)
        )
        issues.extend(
            self.violation(
                f"Kanban task '{item.id}' has unsupported priority '{item.priority}'.",
                path=f"elements.{item.id}",
            )
            for item in diagram.walk_elements()
            if isinstance(item, Task) and item.priority and item.priority not in priorities
        )
        return tuple(issues)
