from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import Column, Task
from .constraint import KanbanDiagramConstraint


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
