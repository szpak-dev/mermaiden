
from wireup import injectable

from ...core.constraint import ConstraintDiagram, Violation
from ..domain import DiagramConstraint
from .elements import PacketField


class PacketConstraint(DiagramConstraint):
    pass



@injectable(as_type=PacketConstraint, qualifier="packet_structure")
class PacketStructure(PacketConstraint):


    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Packet field '{item.id}' must define a range or bit count.",
                path=f"elements.{item.id}",
            )
            for item in diagram.root_elements
            if isinstance(item, PacketField) and item.bits is None and item.start is None
        )
