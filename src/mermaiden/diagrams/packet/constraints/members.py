from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..elements import PacketField
from .constraint import PacketConstraint


@injectable(as_type=PacketConstraint, qualifier="packet_members")
class PacketMembers(DiagramMembersConstraint, PacketConstraint):
    element_types: ClassVar = (PacketField,)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "a packet field"
    relation_description: ClassVar[str] = "valid in a packet diagram"
    annotation_description: ClassVar[str] = "valid in a packet diagram"

    @property
    def code(self) -> str:
        return "packet.member_type"
