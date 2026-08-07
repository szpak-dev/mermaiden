from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..elements import Component, Evolution, Pipeline
from ..relations import Dependency
from .constraint import WardleyDiagramConstraint


@injectable(as_type=WardleyDiagramConstraint, qualifier="wardley_members")
class WardleyDiagramMembers(DiagramMembersConstraint, WardleyDiagramConstraint):
    element_types: ClassVar = (Component, Evolution, Pipeline,)
    relation_types: ClassVar = (Dependency,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Wardley map"
    relation_description: ClassVar[str] = "valid in Wardley map"
    annotation_description: ClassVar[str] = "valid in Wardley map"

    @property
    def code(self) -> str:
        return "wardley.member_type"
