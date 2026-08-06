from collections import defaultdict
from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import Violation
from ....core.diagram import Diagram
from ..elements import Decision, End, FlowNode, Start
from ..relations import Flow
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="node_degree_rules")
@dataclass(frozen=True, slots=True)
class NodeDegreeRules(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.node_degree"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        incoming: defaultdict[str, list[Flow]] = defaultdict(list)
        outgoing: defaultdict[str, list[Flow]] = defaultdict(list)
        for flow in self.flows(diagram):
            incoming[flow.target_id].append(flow)
            outgoing[flow.source_id].append(flow)
        issues: list[Violation] = []
        for node in diagram.walk_elements():
            if isinstance(node, Start):
                issues.extend(self._expect(node.id, len(incoming[node.id]), 0, 0, "incoming"))
                issues.extend(self._expect(node.id, len(outgoing[node.id]), 1, 1, "outgoing"))
            elif isinstance(node, End):
                issues.extend(self._expect(node.id, len(incoming[node.id]), 1, None, "incoming"))
                issues.extend(self._expect(node.id, len(outgoing[node.id]), 0, 0, "outgoing"))
            elif isinstance(node, Decision):
                issues.extend(self._expect(node.id, len(incoming[node.id]), 1, 1, "incoming"))
                issues.extend(self._expect(node.id, len(outgoing[node.id]), 2, None, "outgoing"))
            elif isinstance(node, FlowNode):
                issues.extend(self._expect(node.id, len(incoming[node.id]), 1, None, "incoming"))
                issues.extend(self._expect(node.id, len(outgoing[node.id]), 1, 1, "outgoing"))
        return tuple(issues)

    def _expect(
        self, node_id: str, actual: int, minimum: int, maximum: int | None, direction: str
    ) -> list[Violation]:
        if actual >= minimum and (maximum is None or actual <= maximum):
            return []
        if maximum is None:
            expected = f"at least {minimum}"
        elif minimum == maximum:
            expected = str(minimum)
        else:
            expected = f"{minimum}..{maximum}"
        return [
            self.violation(
                f"Node '{node_id}' requires {expected} {direction} flow(s); found {actual}.",
                path=f"elements.{node_id}",
            )
        ]
