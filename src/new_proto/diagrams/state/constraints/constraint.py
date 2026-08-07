from abc import ABC

from ....core.constraint import Constraint, ConstraintDiagram
from ..relations import StateTransition


class StateDiagramConstraint(Constraint, ABC):
    @staticmethod
    def transitions(diagram: ConstraintDiagram) -> tuple[StateTransition, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, StateTransition))
