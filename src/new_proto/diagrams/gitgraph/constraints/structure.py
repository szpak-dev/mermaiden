from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from .constraint import GitGraphDiagramConstraint


@injectable(as_type=GitGraphDiagramConstraint, qualifier="gitgraph_structure")
class GitGraphDiagramStructure(GitGraphDiagramConstraint):
    @property
    def code(self) -> str:
        return "gitgraph.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
