from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..base import DiagramModel
from .configuration import PacketConfiguration
from .constraints.constraint import PacketConstraint
from .elements import PacketField


@injectable(as_type=DiagramModel, qualifier="packet", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Packet(DiagramModel):
    constraints: Sequence[PacketConstraint]
    configuration: PacketConfiguration = field(default_factory=PacketConfiguration, init=False)
    title: str = field(default="", init=False)
    syntax: ClassVar[str] = "packet"
    name: ClassVar[str] = "Packet diagram"
    config_key: ClassVar[str] = "packet"
    schema_definition: ClassVar[str] = "PacketDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}

    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def add_field(self, id: str, label: str, start: int, end: int | None = None) -> ChangeReport:
        return self._add_element(f"add field '{id}'", PacketField(id, label, start, end))

    def add_bits(self, id: str, label: str, bits: int) -> ChangeReport:
        return self._add_element(f"add field '{id}'", PacketField(id, label, None, None, bits))
