from collections import defaultdict
from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import Violation
from ....core.diagram import Diagram
from ..elements import Decision, End, FlowNode, Junction, Start
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
            elif isinstance(node, Junction):
                issues.extend(
                    self._expect_junction(
                        node.id,
                        len(incoming[node.id]),
                        len(outgoing[node.id]),
                    )
                )
            elif isinstance(node, FlowNode):
                issues.extend(self._expect(node.id, len(incoming[node.id]), 1, None, "incoming"))
                issues.extend(self._expect(node.id, len(outgoing[node.id]), 1, 1, "outgoing"))
        return tuple(issues)

    def _expect_junction(self, node_id: str, incoming: int, outgoing: int) -> list[Violation]:
        is_merge = incoming >= 2 and outgoing == 1
        is_split = incoming == 1 and outgoing >= 2
        if is_merge or is_split:
            return []
        return [
            self.violation(
                f"Junction '{node_id}' must merge multiple flows or split one flow; "
                f"found {incoming} incoming and {outgoing} outgoing.",
                path=f"elements.{node_id}",
            )
        ]

    def _expect(self, node_id: str, actual: int, minimum: int, maximum: int | None, direction: str) -> list[Violation]:
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
