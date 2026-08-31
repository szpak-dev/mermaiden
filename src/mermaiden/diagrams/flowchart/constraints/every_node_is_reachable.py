from collections import defaultdict, deque

from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..elements import FlowNode, Start
from .domain import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="every_node_is_reachable")
class EveryNodeIsReachable(FlowchartConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        starts = [item for item in diagram.walk_elements() if isinstance(item, Start)]
        if len(starts) != 1:
            return ()
        adjacency: defaultdict[str, list[str]] = defaultdict(list)
        for flow in self.flows(diagram):
            adjacency[flow.source_id].append(flow.target_id)
        reached = {starts[0].id}
        pending = deque(reached)
        while pending:
            for target in adjacency[pending.popleft()]:
                if target not in reached:
                    reached.add(target)
                    pending.append(target)
        return tuple(
            self.violation(f"Node '{node.id}' is unreachable from the start.", path=f"elements.{node.id}")
            for node in diagram.walk_elements()
            if isinstance(node, FlowNode) and node.id not in reached
        )
