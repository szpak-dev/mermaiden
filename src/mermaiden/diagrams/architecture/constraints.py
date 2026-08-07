from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint
from ..domain import DiagramMembersConstraint
from .annotations import ArchitectureNote
from .elements import ArchitectureGroup, Junction, Service
from .relations import Edge


class ArchitectureConstraint(Constraint):
    pass


@injectable(as_type=ArchitectureConstraint, qualifier="architecture_members")
class ArchitectureMembers(DiagramMembersConstraint, ArchitectureConstraint):
    element_types: ClassVar = (ArchitectureGroup, Service, Junction)
    relation_types: ClassVar = (Edge,)
    annotation_types: ClassVar = (ArchitectureNote,)
    element_description: ClassVar[str] = "an architecture member"
    relation_description: ClassVar[str] = "an architecture edge"
    annotation_description: ClassVar[str] = "an architecture note"

    @property
    def code(self) -> str:
        return "architecture.members"
