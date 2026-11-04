from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="packet_structure")
class PacketConstraint(DiagramConstraint):
    pass
