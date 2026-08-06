from ....core.constraint import Constraint
from ....core.diagram import Diagram
from ..relations import Flow


class FlowchartConstraint(Constraint):
    @staticmethod
    def flows(diagram: Diagram) -> tuple[Flow, ...]:
        return tuple(item for item in diagram.relations if isinstance(item, Flow))
