from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import Swimlane, SwimlaneNode
from ..relations import Flow
from .constraint import SwimlaneConstraint


@injectable(as_type=SwimlaneConstraint, qualifier="swimlane_members")
class SwimlaneContainsOnlySwimlaneMembers(DiagramMembersConstraint, SwimlaneConstraint):
    element_types: ClassVar = (Swimlane, SwimlaneNode)
    relation_types: ClassVar = (Flow,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a swimlane diagram"
    relation_description: ClassVar[str] = "a swimlane flow"
    annotation_description: ClassVar[str] = "valid in a swimlane diagram"

    @property
    def code(self) -> str:
        return "swimlane.member_type"
