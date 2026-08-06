from ...core.constraint import Constraint, ElementPresence
from .elements import Start


class FlowchartConstraint(Constraint):
    pass


class ExactlyOneStart(FlowchartConstraint, ElementPresence):
    @property
    def element(self) -> type[Start]:
        return Start

    @property
    def minimum(self) -> int:
        return 1

    @property
    def maximum(self) -> int:
        return 1
