from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import Domain
from ..relations import Transition
from .constraint import CynefinDiagramConstraint


@injectable(as_type=CynefinDiagramConstraint, qualifier="cynefin_members")
class CynefinDiagramMembers(DiagramMembersConstraint, CynefinDiagramConstraint):
    element_types: ClassVar = (Domain,)
    relation_types: ClassVar = (Transition,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Cynefin diagram"
    relation_description: ClassVar[str] = "valid in Cynefin diagram"
    annotation_description: ClassVar[str] = "valid in Cynefin diagram"

    @property
    def code(self) -> str:
        return "cynefin.member_type"
