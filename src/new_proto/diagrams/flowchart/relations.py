from new_proto.interface import Interface

from ...core.relation import DirectedRelation
from .elements import FlowNode


class Flow(DirectedRelation):
    @Interface.prop
    def source(self) -> FlowNode: ...

    @Interface.prop
    def target(self) -> FlowNode: ...
