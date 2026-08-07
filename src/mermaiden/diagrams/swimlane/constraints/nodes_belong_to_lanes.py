from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..elements import SwimlaneNode
from .constraint import SwimlaneConstraint


@injectable(as_type=SwimlaneConstraint, qualifier="nodes_belong_to_lanes")
class NodesBelongToLanes(SwimlaneConstraint):
    @property
    def code(self) -> str:
        return "swimlane.node_lane"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(f"Node '{node.id}' must belong to a lane.", path=f"elements.{node.id}")
            for node in diagram.root_elements
            if isinstance(node, SwimlaneNode)
        )
