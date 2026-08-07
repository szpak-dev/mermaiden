from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import DiagramMembersConstraint
from .elements import Column, Task


class KanbanDiagramConstraint(Constraint, ABC):
    pass

@injectable(as_type=KanbanDiagramConstraint, qualifier="kanban_members")
class KanbanDiagramMembers(DiagramMembersConstraint, KanbanDiagramConstraint):
    element_types: ClassVar = (Task, Column,)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Kanban diagram"
    relation_description: ClassVar[str] = "valid in Kanban diagram"
    annotation_description: ClassVar[str] = "valid in Kanban diagram"

    @property
    def code(self) -> str:
        return "kanban.member_type"

@injectable(as_type=KanbanDiagramConstraint, qualifier="kanban_structure")
class KanbanDiagramStructure(KanbanDiagramConstraint):
    @property
    def code(self) -> str:
        return "kanban.structure"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

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
