from ....core.domain import ConstraintDiagram
from ...domain import DiagramConstraint
from ..relations import StateTransition


class StateDiagramConstraint(DiagramConstraint):
    def transitions(self, diagram: ConstraintDiagram) -> tuple[StateTransition, ...]:
        return tuple(item for item in diagram.find_relations("") if isinstance(item, StateTransition))
