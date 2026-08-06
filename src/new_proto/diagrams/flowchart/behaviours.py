from new_proto.core import Behaviour

from .model import Action, Decision, End, FlowNode, Flowchart, Group, Outcome, Start


class RenameNode(Behaviour):
    @property
    def name(self) -> str:
        return "rename_node"

    def execute(self, *, label: str) -> FlowNode:
        owner = self.owner
        assert isinstance(owner, FlowNode)
        owner.rename(label)
        return owner


class AddStart(Behaviour):
    name = "add_start"

    def execute(self, *, label: str, node_id: str | None = None, parent_id: str | None = None) -> Start:
        assert isinstance(self.owner, Flowchart)
        return self.owner.add_start(label, node_id=node_id, parent_id=parent_id)


class AddEnd(AddStart):
    name = "add_end"

    def execute(self, *, label: str, node_id: str | None = None, parent_id: str | None = None) -> End:
        assert isinstance(self.owner, Flowchart)
        return self.owner.add_end(label, node_id=node_id, parent_id=parent_id)


class AddAction(AddStart):
    name = "add_action"

    def execute(self, *, label: str, node_id: str | None = None, parent_id: str | None = None) -> Action:
        assert isinstance(self.owner, Flowchart)
        return self.owner.add_action(label, node_id=node_id, parent_id=parent_id)


class AddDecision(AddStart):
    name = "add_decision"

    def execute(self, *, question: str, node_id: str | None = None, parent_id: str | None = None) -> Decision:
        assert isinstance(self.owner, Flowchart)
        return self.owner.add_decision(question, node_id=node_id, parent_id=parent_id)


class AddGroup(AddStart):
    name = "add_group"

    def execute(self, *, label: str, group_id: str | None = None, parent_id: str | None = None) -> Group:
        assert isinstance(self.owner, Flowchart)
        return self.owner.add_group(label, group_id=group_id, parent_id=parent_id)


class Connect(Behaviour):
    name = "connect"

    def execute(self, *, source_id: str, target_id: str, outcome: Outcome = Outcome.NEXT, label: str = ""):
        assert isinstance(self.owner, Flowchart)
        return self.owner.connect(source_id, target_id, outcome=outcome, label=label)


class AddBranch(Behaviour):
    name = "add_branch"

    def execute(self, *, outcome: Outcome, target_id: str, label: str = ""):
        assert isinstance(self.owner, Decision)
        return self.owner.branch(outcome, target_id, label=label)
