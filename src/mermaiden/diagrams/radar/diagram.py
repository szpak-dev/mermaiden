from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .configuration import RadarConfiguration
from .constraints import RadarAnnotationMember, RadarConstraint, RadarRelationMember
from .elements import RadarAxis, RadarCurve, RadarElementMember


@injectable(as_type=DiagramModel, qualifier="radar", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Radar(DiagramModel):
    constraints: Sequence[RadarConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "radar.member_type",
        RadarElementMember,
        RadarRelationMember,
        RadarAnnotationMember,
    )
    configuration: RadarConfiguration = field(default_factory=RadarConfiguration, init=False)
    title: str = field(default="", init=False)
    show_legend: bool = field(default=True, init=False)
    minimum: float | None = field(default=None, init=False)
    maximum: float | None = field(default=None, init=False)
    graticule: str = field(default="circle", init=False)
    ticks: int | None = field(default=None, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "radar-beta",
        "Radar chart",
        "radar",
        "RadarDiagramConfig",
    )


    def set_title(self, title: str) -> None:
        object.__setattr__(self, "title", title)

    def set_legend(self, visible: bool) -> None:
        object.__setattr__(self, "show_legend", visible)

    def set_range(self, minimum: float, maximum: float) -> None:
        object.__setattr__(self, "minimum", minimum)
        object.__setattr__(self, "maximum", maximum)

    def set_graticule(self, graticule: str) -> None:
        object.__setattr__(self, "graticule", graticule)

    def set_ticks(self, ticks: int) -> None:
        object.__setattr__(self, "ticks", ticks)

    def add_axis(self, id: str, label: str) -> ChangeReport:
        return self._add_element(f"add axis '{id}'", RadarAxis(id, label))

    def add_curve(self, id: str, label: str, values: tuple[float, ...]) -> ChangeReport:
        return self._add_element(f"add curve '{id}'", RadarCurve(id, label, values))
