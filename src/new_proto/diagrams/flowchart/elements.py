from .base import FlowNode


class StartNode(FlowNode):
    pass


class TerminationNode(FlowNode):
    pass


class DecisionNode(FlowNode):
    pass


class ActionNode(FlowNode):
    pass


class SubprocessNode(ActionNode):
    pass


class ManualOperationNode(ActionNode):
    pass


class PreparationNode(ActionNode):
    pass


class ForkJoinNode(FlowNode):
    pass


class JunctionNode(FlowNode):
    pass


class InputNode(FlowNode):
    pass


class ManualInputNode(InputNode):
    pass


class OutputNode(FlowNode):
    pass


class DisplayNode(OutputNode):
    pass


class DocumentNode(FlowNode):
    pass


class MultipleDocumentsNode(DocumentNode):
    pass


class DataStoreNode(FlowNode):
    pass


class DatabaseNode(DataStoreNode):
    pass


class DelayNode(FlowNode):
    pass
