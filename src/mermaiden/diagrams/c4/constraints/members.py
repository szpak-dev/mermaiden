from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import Person, System, SystemDb, SystemQueue
from ..relations import Relationship
from .constraint import C4ContextDiagramConstraint


@injectable(as_type=C4ContextDiagramConstraint, qualifier="c4_members")
class C4ContextDiagramMembers(DiagramMembersConstraint, C4ContextDiagramConstraint):
    element_types: ClassVar = (Person, System, SystemDb, SystemQueue,)
    relation_types: ClassVar = (Relationship,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in C4 Context diagram"
    relation_description: ClassVar[str] = "valid in C4 Context diagram"
    annotation_description: ClassVar[str] = "valid in C4 Context diagram"

    @property
    def code(self) -> str:
        return "c4.member_type"
