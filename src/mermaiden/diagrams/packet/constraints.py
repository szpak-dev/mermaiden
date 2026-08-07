from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import (
    DiagramAnnotationMember,
    DiagramRelationMember,
)
from .elements import PacketField


class PacketConstraint(Constraint, ABC):
    pass

class PacketRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "valid in a packet diagram"


class PacketAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in a packet diagram"


@injectable(as_type=PacketConstraint, qualifier="packet_structure")
class PacketStructure(PacketConstraint):
    @property
    def code(self) -> str:
        return "packet.structure"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return tuple(
            self.violation(
                f"Packet field '{item.id}' must define a range or bit count.",
                path=f"elements.{item.id}",
            )
            for item in diagram.root_elements
            if isinstance(item, PacketField) and item.bits is None and item.start is None
        )
