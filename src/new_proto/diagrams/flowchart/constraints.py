from wireup import injectable

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


@injectable(as_type=Constraint, qualifier="exactly_one_start")
class ExactlyOneStart(ExactlyOne):
    element_type = Start


@injectable(as_type=Constraint, qualifier="exactly_one_termination")
class ExactlyOneTermination(ExactlyOne):
    element_type = Termination


@injectable(as_type=Constraint, qualifier="start_has_no_incoming")
class StartHasNoIncoming(NoIncoming):
    element_type = Start
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="start_has_single_outgoing")
class StartHasSingleOutgoing(SingleOutgoing):
    element_type = Start
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="termination_has_incoming")
class TerminationHasIncoming(AtLeastOneIncoming):
    element_type = Termination
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="termination_has_no_outgoing")
class TerminationHasNoOutgoing(NoOutgoing):
    element_type = Termination
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="fork_has_single_incoming")
class ForkHasSingleIncoming(SingleIncoming):
    element_type = Fork
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="fork_has_multiple_outgoing")
class ForkHasMultipleOutgoing(MultipleOutgoing):
    element_type = Fork
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="join_has_multiple_incoming")
class JoinHasMultipleIncoming(MultipleIncoming):
    element_type = Join
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="join_has_single_outgoing")
class JoinHasSingleOutgoing(SingleOutgoing):
    element_type = Join
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="decision_has_single_incoming")
class DecisionHasSingleIncoming(SingleIncoming):
    element_type = Decision
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="decision_has_multiple_outgoing")
class DecisionHasMultipleOutgoing(MultipleOutgoing):
    element_type = Decision
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="decision_branches_are_conditioned")
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


@injectable(as_type=Constraint, qualifier="linear_node_has_incoming")
class LinearNodeHasIncoming(AtLeastOneIncoming):
    element_type = LinearNode
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="linear_node_has_single_outgoing")
class LinearNodeHasSingleOutgoing(SingleOutgoing):
    element_type = LinearNode
    relation_type = Flow


@injectable(as_type=Constraint, qualifier="parallel_regions_are_paired")
class ParallelRegionsArePaired(Constraint):
    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool:
        regions = tuple(
            relation
            for relation in diagram_contents.relations
            if isinstance(relation, ParallelRegion)
        )
        forks = tuple(element for element in diagram_contents.elements if isinstance(element, Fork))
        joins = tuple(element for element in diagram_contents.elements if isinstance(element, Join))
        return all(sum(region.fork is fork for region in regions) == 1 for fork in forks) and all(
            sum(region.join is join for region in regions) == 1 for join in joins
        )


class ParallelRegionRule(Constraint):
    def _flows(self, diagram_contents: DiagramContents) -> tuple[Flow, ...]:
        return tuple(
            relation for relation in diagram_contents.relations if isinstance(relation, Flow)
        )

    def _regions(self, diagram_contents: DiagramContents) -> tuple[ParallelRegion, ...]:
        return tuple(
            relation
            for relation in diagram_contents.relations
            if isinstance(relation, ParallelRegion)
        )

    def _reaches(
        self,
        source: FlowNode,
        target: FlowNode,
        flows: tuple[Flow, ...],
        visited: tuple[FlowNode, ...] = (),
    ) -> bool:
        if source is target:
            return True
        if any(source is seen for seen in visited):
            return False
        return any(
            self._reaches(flow.target, target, flows, (*visited, source))
            for flow in flows
            if flow.source is source
        )


@injectable(as_type=Constraint, qualifier="fork_branches_reach_join")
class ForkBranchesReachJoin(ParallelRegionRule):
    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool:
        flows = self._flows(diagram_contents)
        return all(self._region_reaches_join(region, flows) for region in self._regions(diagram_contents))

    def _region_reaches_join(self, region: ParallelRegion, flows: tuple[Flow, ...]) -> bool:
        branches = tuple(flow.target for flow in flows if flow.source is region.fork)
        return bool(branches) and all(
            self._reaches(branch, region.join, flows) for branch in branches
        )


@injectable(as_type=Constraint, qualifier="join_inputs_come_from_fork")
class JoinInputsComeFromFork(ParallelRegionRule):
    def is_satisfied_by(self, diagram_contents: DiagramContents) -> bool:
        flows = self._flows(diagram_contents)
        return all(
            all(
                self._reaches(region.fork, flow.source, flows)
                for flow in flows
                if flow.target is region.join
            )
            for region in self._regions(diagram_contents)
        )
