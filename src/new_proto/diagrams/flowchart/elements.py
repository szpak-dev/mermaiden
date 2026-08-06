from new_proto.interface import Interface

from ...core.element import Container, Entity


class FlowNode(Entity):
    pass


class FlowNodeGroup(Entity, Container):
    @Interface.prop
    def children(self) -> tuple[FlowNode, ...]: ...


class Start(FlowNode):
    pass


class Termination(FlowNode):
    pass


class Decision(FlowNode):
    pass


class Action(FlowNode):
    pass


class Subprocess(Action):
    pass


class ManualOperation(Action):
    pass


class Preparation(Action):
    pass


class ForkJoin(FlowNode):
    pass


class Junction(FlowNode):
    pass


class Input(FlowNode):
    pass


class ManualInput(Input):
    pass


class Output(FlowNode):
    pass


class Display(Output):
    pass


class Document(FlowNode):
    pass


class MultipleDocuments(Document):
    pass


class DataStore(FlowNode):
    pass


class Database(DataStore):
    pass


class Delay(FlowNode):
    pass
