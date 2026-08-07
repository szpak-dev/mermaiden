from abc import ABC

from ....core.constraint import Constraint
from ....core.diagram import Diagram
from ..relations import TreeBranch


class TreeViewConstraint(Constraint, ABC):
    @staticmethod
    def branches(diagram: Diagram) -> tuple[TreeBranch, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, TreeBranch))
