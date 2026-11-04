from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated, ClassVar

from pydantic import Field
from wireup import injectable

from ...core.characters import Identifier, OptionalText, Text
from ...core.domain import ChangeReport, Container, Element
from ..domain import (
    CommandDefault,
    DiagramCommandFeature,
    DiagramDefinition,
    DiagramFeature,
    DiagramModel,
    PersistedDiagramProperty,
)
from .configuration import PacketConfiguration
from .constraints import PacketConstraint
from .elements import PacketBitCount, PacketField, PacketPosition, PacketRange


@injectable(as_type=DiagramModel, qualifier="packet", lifetime="transient")
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

    feature: ClassVar[DiagramFeature] = DiagramFeature(
        configuration=PacketConfiguration,
        snapshot_properties=(
            PersistedDiagramProperty(
                "title",
                Annotated[str, Field(pattern=OptionalText.pattern, description=OptionalText.description)],
            ),
        ),
        elements=(PacketField,),
        relations=(),
        annotations=(),
        commands=(
            DiagramCommandFeature("set_title", {"title": Text}),
            DiagramCommandFeature(
                "add_field", {"id": Identifier, "label": Text, "start": int, "end": CommandDefault(int | None, None)}
            ),
            DiagramCommandFeature("add_bits", {"id": Identifier, "label": Text, "bits": int}),
        ),
    )

    def accepts_parent(self, element_type: type[Element], parent_type: type[Container] | None) -> bool:
        return element_type is PacketField and parent_type is None

    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def add_field(self, id: str, label: str, start: int, end: int | None = None) -> ChangeReport:
        position = PacketPosition(root=PacketRange(kind="range", start=start, end=start if end is None else end))
        return self._add_element(f"add field '{id}'", PacketField(id=id, label=label, position=position))

    def add_bits(self, id: str, label: str, bits: int) -> ChangeReport:
        position = PacketPosition(root=PacketBitCount(kind="bits", bits=bits))
        return self._add_element(f"add field '{id}'", PacketField(id=id, label=label, position=position))
