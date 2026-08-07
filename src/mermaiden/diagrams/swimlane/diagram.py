from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from ..flowchart.elements import Direction
from .configuration import SwimlaneConfiguration
from .constraints import SwimlaneAnnotationMember, SwimlaneConstraint
from .elements import Activity, Connector, Decision, End, Start, Swimlane, SwimlaneElementMember, SwimlaneNode
from .relations import ConditionalFlow, Flow, SwimlaneRelationMember


@injectable(as_type=DiagramModel, qualifier="swimlane", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class SwimlaneDiagram(DiagramModel):
    constraints: Sequence[SwimlaneConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "swimlane.member_type",
        SwimlaneElementMember,
        SwimlaneRelationMember,
        SwimlaneAnnotationMember,
    )
    configuration: SwimlaneConfiguration = field(default_factory=SwimlaneConfiguration, init=False)
    direction: Direction = field(default=Direction.TOP_DOWN, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "swimlane-beta",
        "Swimlane diagram",
        "swimlane",
        "SwimlaneDiagramConfig",
    )


    def add_lane(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add lane '{id}'", Swimlane(id, label))

    def add_activity(self, id: str, label: str, lane_id: str) -> ChangeReport:
        return self._add_node(Activity(id, label), lane_id, "activity")

    def add_start(self, id: str, label: str, lane_id: str) -> ChangeReport:
        return self._add_node(Start(id, label), lane_id, "start")

    def add_end(self, id: str, label: str, lane_id: str) -> ChangeReport:
        return self._add_node(End(id, label), lane_id, "end")

    def add_decision(self, id: str, label: str, lane_id: str) -> ChangeReport:
        return self._add_node(Decision(id, label), lane_id, "decision")

    def add_connector(self, id: str, label: str, lane_id: str) -> ChangeReport:
        return self._add_node(Connector(id, label), lane_id, "connector")

    def add_flow(self, id: str, source_id: str, target_id: str, label: str = "") -> ChangeReport:
        return self._add_relation(f"add flow '{id}'", Flow(id, (source_id, target_id), label))

    def add_conditional_flow(self, id: str, source_id: str, target_id: str, condition: str) -> ChangeReport:
        return self._add_relation(
            f"add conditional flow '{id}'",
            ConditionalFlow(id, (source_id, target_id), condition),
        )

    def remove_flow(self, id: str) -> ChangeReport:
        return self.remove_relation(id)

    def _add_node(self, node: SwimlaneNode, lane_id: str, kind: str) -> ChangeReport:
        return self._add_element(f"add {kind} '{node.id}'", node, lane_id)
