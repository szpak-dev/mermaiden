from dataclasses import dataclass
from typing import ClassVar

from ...core.element import Entity


@dataclass(frozen=True, slots=True)
class RadarAxis(Entity):
    kind: ClassVar[str] = "radar_axis"


@dataclass(frozen=True, slots=True)
class RadarCurve(Entity):
    kind: ClassVar[str] = "radar_curve"
    values: tuple[float, ...] = ()
