from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..elements import Actor, Command, Event, Swimlane, View
from ..relations import Flow
from .constraint import EventModelingDiagramConstraint


@injectable(as_type=EventModelingDiagramConstraint, qualifier="eventmodeling_members")
class EventModelingDiagramMembers(DiagramMembersConstraint, EventModelingDiagramConstraint):
    element_types: ClassVar = (Event, Command, View, Actor, Swimlane,)
    relation_types: ClassVar = (Flow,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Event Modeling diagram"
    relation_description: ClassVar[str] = "valid in Event Modeling diagram"
    annotation_description: ClassVar[str] = "valid in Event Modeling diagram"

    @property
    def code(self) -> str:
        return "eventmodeling.member_type"
