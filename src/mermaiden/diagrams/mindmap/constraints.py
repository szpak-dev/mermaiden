from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import MindmapNode


class MindmapConstraint(Constraint, ABC):
    pass

@injectable(as_type=MindmapConstraint, qualifier="mindmap_root")
class ExactlyOneRoot(MindmapConstraint):
    @property
    def code(self) -> str:
        return "mindmap.one_root"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        count = sum(isinstance(item, MindmapNode) for item in diagram.root_elements)
        if count == 1:
            return ()
        return (self.violation(f"Mindmap requires exactly one root; found {count}."),)

@injectable(as_type=MindmapConstraint, qualifier="mindmap_members")
class MindmapContainsOnlyMindmapMembers(DiagramMembersConstraint, MindmapConstraint):
    element_types: ClassVar = (MindmapNode,)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "a mindmap node"
    relation_description: ClassVar[str] = "valid in a mindmap"
    annotation_description: ClassVar[str] = "valid in a mindmap"

    @property
    def code(self) -> str:
        return "mindmap.member_type"
