from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity
from ..domain import DiagramElementMember


class RadarElementMember(DiagramElementMember):
    description: ClassVar[str] = "valid in a radar chart"


@dataclass(frozen=True, slots=True)
class RadarAxis(Entity, RadarElementMember):
    kind: ClassVar[str] = "radar_axis"


@dataclass(frozen=True, slots=True)
class RadarCurve(Entity, RadarElementMember):
    kind: ClassVar[str] = "radar_curve"
    values: tuple[float, ...] = ()
