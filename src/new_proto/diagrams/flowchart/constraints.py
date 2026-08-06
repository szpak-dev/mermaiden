from ...core.constraint import Constraint, ElementPresence
from .elements import Start


class FlowchartConstraint(Constraint):
    pass


class ExactlyOneStart(FlowchartConstraint, ElementPresence):
    element = Start
    minimum = 1
    maximum = 1
