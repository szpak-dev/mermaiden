from typing import ClassVar

from wireup import injectable

from ...base import DiagramMembersConstraint
from ..elements import Alternative, Group, NonTerminal, Optional, Repetition, Sequence, Special, Terminal
from .constraint import RailroadDiagramConstraint


@injectable(as_type=RailroadDiagramConstraint, qualifier="railroad_members")
class RailroadDiagramMembers(DiagramMembersConstraint, RailroadDiagramConstraint):
    element_types: ClassVar = (Terminal, NonTerminal, Special, Sequence, Alternative, Optional, Repetition, Group)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Railroad diagram"
    relation_description: ClassVar[str] = "valid in Railroad diagram"
    annotation_description: ClassVar[str] = "valid in Railroad diagram"

    @property
    def code(self) -> str:
        return "railroad.member_type"
