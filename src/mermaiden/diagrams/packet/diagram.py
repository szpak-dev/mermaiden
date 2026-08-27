from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramModel
from .configuration import PacketConfiguration
from .constraints import PacketConstraint
from .elements import PacketField


@injectable(as_type=DiagramModel, qualifier="packet", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Packet(DiagramModel):
    constraints: Sequence[PacketConstraint]
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
        return self._add_element(f"add field '{id}'", PacketField(id=id, label=label, start=start, end=end))

    def add_bits(self, id: str, label: str, bits: int) -> ChangeReport:
        return self._add_element(f"add field '{id}'", PacketField(id=id, label=label, start=None, end=None, bits=bits))
