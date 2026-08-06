from ..elements import FlowNode
from ..relations import Flow


class FlowElement(Flow):
    def __init__(self, source: FlowNode, target: FlowNode):
        self._source = source
        self._target = target

    @property
    def source(self) -> FlowNode:
        return self._source

    @property
    def target(self) -> FlowNode:
        return self._target
