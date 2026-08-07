from collections import defaultdict, deque
from typing import ClassVar

from wireup import injectable

from ...core.annotation import TargetKind
from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import DiagramMembersConstraint
from .annotations import Note
from .elements import Decision, End, FlowGroup, FlowNode, Junction, Start
from .relations import ConditionalFlow, Flow


class FlowchartConstraint(Constraint):
    @staticmethod
    def flows(diagram: ConstraintDiagram) -> tuple[Flow, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, Flow))

@injectable(as_type=FlowchartConstraint, qualifier="conditional_flows_have_conditions")
class ConditionalFlowsHaveConditions(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.conditional_flow_condition"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Conditional flow '{flow.id}' requires a condition.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if isinstance(flow, ConditionalFlow) and not flow.condition.strip()
        )

@injectable(as_type=FlowchartConstraint, qualifier="decision_branches_are_conditioned")
class DecisionBranchesAreConditioned(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.decision_conditions"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues: list[Violation] = []
        flows = self.flows(diagram)
        for decision in (item for item in diagram.walk_elements() if isinstance(item, Decision)):
            branches = tuple(flow for flow in flows if flow.source_id == decision.id)
            conditions = [flow.condition.strip() for flow in branches if isinstance(flow, ConditionalFlow)]
            if len(conditions) != len(branches) or any(not item for item in conditions):
                issues.append(
                    self.violation(
                        f"Every branch from decision '{decision.id}' needs a condition.",
                        path=f"elements.{decision.id}",
                    )
                )
            elif len(set(conditions)) != len(conditions):
                issues.append(
                    self.violation(
                        f"Decision '{decision.id}' has duplicate conditions.",
                        path=f"elements.{decision.id}",
                    )
                )
        return tuple(issues)

@injectable(as_type=FlowchartConstraint, qualifier="every_node_is_reachable")
class EveryNodeIsReachable(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.reachable"

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

@injectable(as_type=FlowchartConstraint, qualifier="exactly_one_start")
class ExactlyOneStart(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.one_start"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        count = sum(isinstance(item, Start) for item in diagram.walk_elements())
        if count == 1:
            return ()
        return (self.violation(f"Flowchart requires exactly one start; found {count}."),)

@injectable(as_type=FlowchartConstraint, qualifier="flow_endpoints_are_nodes")
class FlowEndpointsAreNodes(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.flow_endpoint"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements()}
        return tuple(
            self.violation(
                f"Flow '{flow.id}' endpoints must both be flow nodes.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if len(flow.element_ids) == 2
            if flow.source_id in elements
            and flow.target_id in elements
            and not (isinstance(elements[flow.source_id], FlowNode) and isinstance(elements[flow.target_id], FlowNode))
        )

@injectable(as_type=FlowchartConstraint, qualifier="flowchart_members")
class FlowchartContainsOnlyFlowchartMembers(DiagramMembersConstraint, FlowchartConstraint):
    element_types: ClassVar = (FlowNode, FlowGroup)
    relation_types: ClassVar = (Flow,)
    annotation_types: ClassVar = (Note,)
    element_description: ClassVar[str] = "a flowchart element"
    relation_description: ClassVar[str] = "a flow"
    annotation_description: ClassVar[str] = "a flowchart note"

    @property
    def code(self) -> str:
        return "flowchart.member_type"

@injectable(as_type=FlowchartConstraint, qualifier="flows_are_binary")
class FlowsAreBinary(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.binary_flow"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Flow '{flow.id}' requires exactly one source and one target.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if len(flow.element_ids) != 2
        )

@injectable(as_type=FlowchartConstraint, qualifier="node_degree_rules")
class NodeDegreeRules(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.node_degree"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
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

@injectable(as_type=FlowchartConstraint, qualifier="notes_are_valid")
class NotesAreValid(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.note"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues: list[Violation] = []
        for note in (item for item in diagram.find_annotations() if isinstance(item, Note)):
            if not note.text.strip():
                issues.append(
                    self.violation(
                        f"Note '{note.id}' requires text.",
                        path=f"annotations.{note.id}",
                    )
                )
            if any(target.kind is not TargetKind.ELEMENT for target in note.targets):
                issues.append(
                    self.violation(
                        f"Note '{note.id}' can only target elements.",
                        path=f"annotations.{note.id}",
                    )
                )
        return tuple(issues)
