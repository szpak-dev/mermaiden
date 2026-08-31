from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..elements import SwimlaneNode
from .domain import SwimlaneConstraint


@injectable(as_type=SwimlaneConstraint, qualifier="nodes_belong_to_lanes")
class NodesBelongToLanes(SwimlaneConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(f"Node '{node.id}' must belong to a lane.", path=f"elements.{node.id}")
            for node in diagram.root_elements
            if isinstance(node, SwimlaneNode)
        )
