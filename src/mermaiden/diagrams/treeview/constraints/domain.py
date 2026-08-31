from ....core.domain import ConstraintDiagram
from ...domain import DiagramConstraint
from ..relations import TreeBranch


class TreeViewConstraint(DiagramConstraint):
    def branches(self, diagram: ConstraintDiagram) -> tuple[TreeBranch, ...]:
        return tuple(item for item in diagram.find_relations("") if isinstance(item, TreeBranch))
