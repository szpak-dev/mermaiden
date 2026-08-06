from ...core.constraint import ElementPresence
from ...diagrams.flowchart.base import FlowNode


class FlowchartConstraint(ElementPresence):
    element: type[FlowNode]


class ExactlyOneStart(FlowchartConstraint):
    pass
