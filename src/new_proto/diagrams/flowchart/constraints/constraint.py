from ....core.constraint import Constraint
from ....core.diagram import Diagram
from ..relations import Flow


class FlowchartConstraint(Constraint):
    @staticmethod
    def flows(diagram: Diagram) -> tuple[Flow, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, Flow))
