from ...runtime.constraints import (
    AtLeastOneIncoming,
    ExactlyOne,
    MultipleIncoming,
    MultipleOutgoing,
    NoIncoming,
    NoOutgoing,
    SingleIncoming,
    SingleOutgoing,
)
from ...core.constraint import Constraint
from ...core.diagram import DiagramContents
from .elements import Decision, FlowNode, Fork, Join, LinearNode, Start, Termination
from .relations import ConditionalFlow, Flow, ParallelRegion


class ExactlyOneStart(ExactlyOne):
    element_type = Start


class StartHasNoIncoming(NoIncoming):
    element_type = Start
    relation_type = Flow


class StartHasSingleOutgoing(SingleOutgoing):
    element_type = Start
    relation_type = Flow


class TerminationHasIncoming(AtLeastOneIncoming):
    element_type = Termination
    relation_type = Flow


class TerminationHasNoOutgoing(NoOutgoing):
    element_type = Termination
    relation_type = Flow


class ForkHasSingleIncoming(SingleIncoming):
    element_type = Fork
    relation_type = Flow


class ForkHasMultipleOutgoing(MultipleOutgoing):
    element_type = Fork
    relation_type = Flow


class JoinHasMultipleIncoming(MultipleIncoming):
    element_type = Join
    relation_type = Flow


class JoinHasSingleOutgoing(SingleOutgoing):
    element_type = Join
    relation_type = Flow


class DecisionHasSingleIncoming(SingleIncoming):
    element_type = Decision
    relation_type = Flow


class DecisionHasMultipleOutgoing(MultipleOutgoing):
    element_type = Decision
    relation_type = Flow


class DecisionBranchesAreConditioned(Constraint):
    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool:
        flows = tuple(
            relation for relation in diagram_contents.relations if isinstance(relation, Flow)
        )
        return all(
            self._branches_are_conditioned(decision, flows)
            for decision in diagram_contents.elements
            if isinstance(decision, Decision)
        )

    def _branches_are_conditioned(self, decision: Decision, flows: tuple[Flow, ...]) -> bool:
        branches = tuple(flow for flow in flows if flow.source is decision)
        conditional_branches = tuple(
            branch for branch in branches if isinstance(branch, ConditionalFlow)
        )
        if len(conditional_branches) != len(branches) or not all(
            branch.condition.strip() for branch in conditional_branches
        ):
            return False
        conditions = tuple(branch.condition for branch in conditional_branches)
        return len(conditions) == len(set(conditions))


class LinearNodeHasIncoming(AtLeastOneIncoming):
    element_type = LinearNode
    relation_type = Flow


class LinearNodeHasSingleOutgoing(SingleOutgoing):
    element_type = LinearNode
    relation_type = Flow


class ForkBranchesCanResolve(Constraint):
    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool:
        flows = tuple(
            relation for relation in diagram_contents.relations if isinstance(relation, Flow)
        )
        regions = tuple(
            relation
            for relation in diagram_contents.relations
            if isinstance(relation, ParallelRegion)
        )
        return all(self._region_can_resolve(region, flows) for region in regions)

    def _region_can_resolve(self, region: ParallelRegion, flows: tuple[Flow, ...]) -> bool:
        branches = tuple(flow.target for flow in flows if flow.source is region.fork)
        return bool(branches) and all(
            self._can_resolve(branch, region.join, flows) for branch in branches
        )

    def _can_resolve(self, node: FlowNode, join: Join, flows: tuple[Flow, ...]) -> bool:
        return self._can_reach(node, join, flows, ())

    def _can_reach(
        self,
        node: FlowNode,
        join: Join,
        flows: tuple[Flow, ...],
        visited: tuple[FlowNode, ...],
    ) -> bool:
        if node is join or isinstance(node, Termination):
            return True
        if any(node is seen for seen in visited):
            return False
        return any(
            self._can_reach(flow.target, join, flows, (*visited, node))
            for flow in flows
            if flow.source is node
        )
