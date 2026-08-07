from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import PacketConfiguration
from .constraints import PacketAnnotationMember, PacketConstraint, PacketRelationMember
from .elements import PacketElementMember, PacketField


@injectable(as_type=DiagramModel, qualifier="packet", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Packet(DiagramModel):
    constraints: Sequence[PacketConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "packet.member_type",
        PacketElementMember,
        PacketRelationMember,
        PacketAnnotationMember,
    )
    configuration: PacketConfiguration = field(default_factory=PacketConfiguration, init=False)
    title: str = field(default="", init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "packet",
        "Packet diagram",
        "packet",
        "PacketDiagramConfig",
    )


    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def add_field(self, id: str, label: str, start: int, end: int | None = None) -> ChangeReport:
        return self._add_element(f"add field '{id}'", PacketField(id, label, start, end))

    def add_bits(self, id: str, label: str, bits: int) -> ChangeReport:
        return self._add_element(f"add field '{id}'", PacketField(id, label, None, None, bits))
