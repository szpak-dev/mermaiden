from wireup import injectable

from ...core.constraint import ConstraintDiagram, Violation
from ..domain import DiagramConstraint
from .elements import Swimlane, SwimlaneNode
from .relations import Flow


class SwimlaneConstraint(DiagramConstraint):
    @staticmethod
    def flows(diagram: ConstraintDiagram) -> tuple[Flow, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, Flow))


@injectable(as_type=SwimlaneConstraint, qualifier="flow_endpoints_are_nodes")
class FlowEndpointsAreNodes(SwimlaneConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements()}
        return tuple(
            self.violation(
                f"Flow '{flow.id}' endpoints must both be swimlane nodes.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if len(flow.element_ids) == 2
            if flow.source_id in elements
            and flow.target_id in elements
            and not (
                isinstance(elements[flow.source_id], SwimlaneNode)
                and isinstance(elements[flow.target_id], SwimlaneNode)
            )
        )


@injectable(as_type=SwimlaneConstraint, qualifier="flows_are_binary")
class FlowsAreBinary(SwimlaneConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Flow '{flow.id}' requires exactly one source and one target.",
                path=f"relations.{flow.id}",
            )
            for flow in self.flows(diagram)
            if len(flow.element_ids) != 2
        )


@injectable(as_type=SwimlaneConstraint, qualifier="lanes_are_top_level")
class LanesAreTopLevel(SwimlaneConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        root_ids = {item.id for item in diagram.root_elements if isinstance(item, Swimlane)}
        return tuple(
            self.violation(f"Lane '{lane.id}' must be top-level.", path=f"elements.{lane.id}")
            for lane in diagram.walk_elements()
            if isinstance(lane, Swimlane) and lane.id not in root_ids
        )


@injectable(as_type=SwimlaneConstraint, qualifier="nodes_belong_to_lanes")
class NodesBelongToLanes(SwimlaneConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(f"Node '{node.id}' must belong to a lane.", path=f"elements.{node.id}")
            for node in diagram.root_elements
            if isinstance(node, SwimlaneNode)
        )
