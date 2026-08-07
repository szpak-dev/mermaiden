
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation
from .elements import MindmapNode


class MindmapConstraint(BlockingConstraint):
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
