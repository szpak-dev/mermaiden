from enum import StrEnum

from new_proto.core import Container, Diagram, Element, Entity, Relation


class Outcome(StrEnum):
    NEXT = "next"
    YES = "yes"
    NO = "no"
    SUCCESS = "success"
    FAILURE = "failure"
    EXCEPTION = "exception"


class FlowNode(Entity):
    def __init__(self, node_id: str, label: str) -> None:
        Element.__init__(self)
        self._id = node_id
        self.label = label

    @property
    def id(self) -> str:
        return self._id

    def rename(self, label: str) -> None:
        self.label = label

    def behaviours(self):
        from .behaviours import RenameNode

        return (*super().behaviours(), RenameNode(self))


class Start(FlowNode):
    @property
    def kind(self) -> str:
        return "start"


class End(FlowNode):
    @property
    def kind(self) -> str:
        return "end"


class Action(FlowNode):
    @property
    def kind(self) -> str:
        return "action"


class Input(FlowNode):
    @property
    def kind(self) -> str:
        return "input"


class Output(FlowNode):
    @property
    def kind(self) -> str:
        return "output"


class DataStore(FlowNode):
    @property
    def kind(self) -> str:
        return "data-store"


class Document(FlowNode):
    @property
    def kind(self) -> str:
        return "document"


class Delay(FlowNode):
    @property
    def kind(self) -> str:
        return "delay"


class Decision(FlowNode):
    @property
    def kind(self) -> str:
        return "decision"

    def branch(self, outcome: Outcome, target_id: str, *, label: str = "") -> Flow:
        diagram = self.root()
        assert isinstance(diagram, Flowchart)
        return diagram.connect(self.id, target_id, outcome=outcome, label=label)

    def behaviours(self):
        from .behaviours import AddBranch

        return (*super().behaviours(), AddBranch(self))


class Group(Entity, Container):
    def __init__(self, group_id: str, label: str) -> None:
        Element.__init__(self)
        self._id = group_id
        self.label = label
        self._init_container()

    @property
    def id(self) -> str:
        return self._id

    @property
    def kind(self) -> str:
        return "group"

    def accepts(self, child: Element) -> bool:
        return isinstance(child, FlowNode | Group)


class Flow(Entity, Relation):
    def __init__(self, flow_id: str, source: str, target: str, outcome: Outcome, label: str = "") -> None:
        Element.__init__(self)
        self._id = flow_id
        self.source = source
        self.target = target
        self.outcome = outcome
        self.label = label

    @property
    def id(self) -> str:
        return self._id

    @property
    def kind(self) -> str:
        return "flow"

    @property
    def endpoints(self) -> tuple[str, ...]:
        return self.source, self.target


class Flowchart(Diagram):
    @property
    def diagram_type(self) -> str:
        return "flowchart"

    def accepts(self, child: Element) -> bool:
        return isinstance(child, FlowNode | Group)

    def _add_node(self, node_type: type[FlowNode], label: str, *, node_id: str | None, parent_id: str | None) -> FlowNode:
        parent: Container = self if parent_id is None else self.find(parent_id)
        if not isinstance(parent, Flowchart | Group):
            raise TypeError("Flowchart nodes can only be added to a group or the diagram root")
        node = node_type(node_id or self.new_id(node_type.__name__.lower()), label)
        parent.add(node)
        return node

    def add_start(self, label: str, *, node_id: str | None = None, parent_id: str | None = None) -> FlowNode:
        return self._add_node(Start, label, node_id=node_id, parent_id=parent_id)

    def add_end(self, label: str, *, node_id: str | None = None, parent_id: str | None = None) -> FlowNode:
        return self._add_node(End, label, node_id=node_id, parent_id=parent_id)

    def add_action(self, label: str, *, node_id: str | None = None, parent_id: str | None = None) -> FlowNode:
        return self._add_node(Action, label, node_id=node_id, parent_id=parent_id)

    def add_decision(self, question: str, *, node_id: str | None = None, parent_id: str | None = None) -> FlowNode:
        return self._add_node(Decision, question, node_id=node_id, parent_id=parent_id)

    def add_group(self, label: str, *, group_id: str | None = None, parent_id: str | None = None) -> Group:
        parent: Container = self if parent_id is None else self.find(parent_id)
        if not isinstance(parent, Flowchart | Group):
            raise TypeError("Flowchart groups can only be added to a group or the diagram root")
        group = Group(group_id or self.new_id("group"), label)
        parent.add(group)
        return group

    def connect(self, source_id: str, target_id: str, *, outcome: Outcome = Outcome.NEXT, label: str = "") -> Flow:
        source = self.find(source_id)
        target = self.find(target_id)
        if not isinstance(source, FlowNode) or not isinstance(target, FlowNode):
            raise TypeError("Flows must connect flowchart nodes")
        flow = Flow(self.new_id("flow"), source.id, target.id, outcome, label)
        self.add_relation(flow)
        return flow

    def behaviours(self):
        from .behaviours import AddAction, AddDecision, AddEnd, AddGroup, AddStart, Connect

        return (*super().behaviours(), AddStart(self), AddEnd(self), AddAction(self), AddDecision(self), AddGroup(self), Connect(self))
