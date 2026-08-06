from ...runtime.elements import IdentifiedContainer, IdentifiedElement


class FlowNode(IdentifiedElement):
    pass


class FlowGroup(IdentifiedContainer):
    pass


class LinearNode(FlowNode):
    pass


class Start(FlowNode):
    pass


class Termination(FlowNode):
    pass


class Decision(FlowNode):
    pass


class Action(LinearNode):
    pass


class Subprocess(Action):
    pass


class ManualOperation(Action):
    pass


class Preparation(Action):
    pass


class Fork(FlowNode):
    pass


class Join(FlowNode):
    pass


class Junction(LinearNode):
    pass


class Input(LinearNode):
    pass


class ManualInput(Input):
    pass


class Output(LinearNode):
    pass


class Display(Output):
    pass


class Document(LinearNode):
    pass


class MultipleDocuments(Document):
    pass


class DataStore(LinearNode):
    pass


class Database(DataStore):
    pass


class Delay(LinearNode):
    pass
