
from wireup import injectable

from ...core.constraint import ConstraintDiagram, Violation
from ..domain import DiagramConstraint
from .elements import Column, KanbanPriority, Task


class KanbanDiagramConstraint(DiagramConstraint):
    pass



@injectable(as_type=KanbanDiagramConstraint, qualifier="kanban_structure")
class KanbanDiagramStructure(KanbanDiagramConstraint):


    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
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
            if isinstance(item, Task) and item.priority and item.priority not in KanbanPriority
        )
        return tuple(issues)
