from collections import defaultdict, deque
from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import Violation
from ....core.diagram import Diagram
from ..elements.elements import FlowNode, Start
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="every_node_is_reachable")
@dataclass(frozen=True, slots=True)
class EveryNodeIsReachable(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.reachable"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        starts = [item for item in diagram.elements if isinstance(item, Start)]
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
            for node in diagram.elements
            if isinstance(node, FlowNode) and node.id not in reached
        )
