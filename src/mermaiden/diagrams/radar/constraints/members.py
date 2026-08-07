from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..elements import RadarAxis, RadarCurve
from .constraint import RadarConstraint


@injectable(as_type=RadarConstraint, qualifier="radar_members")
class RadarMembers(DiagramMembersConstraint, RadarConstraint):
    element_types: ClassVar = (RadarAxis, RadarCurve)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a radar chart"
    relation_description: ClassVar[str] = "valid in a radar chart"
    annotation_description: ClassVar[str] = "valid in a radar chart"

    @property
    def code(self) -> str:
        return "radar.member_type"
