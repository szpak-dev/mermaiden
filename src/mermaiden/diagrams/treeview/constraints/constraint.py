from abc import ABC

from ....core.constraint import Constraint, ConstraintDiagram
from ..relations import TreeBranch


class TreeViewConstraint(Constraint, ABC):
    @staticmethod
    def branches(diagram: ConstraintDiagram) -> tuple[TreeBranch, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, TreeBranch))
