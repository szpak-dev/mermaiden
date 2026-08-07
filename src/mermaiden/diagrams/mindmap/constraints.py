from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)
from .elements import MindmapNode


class MindmapConstraint(Constraint, ABC):
    pass

class MindmapRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in a mindmap"


class MindmapAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a mindmap"


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
