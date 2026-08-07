from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import Requirement, RequirementElement
from ..relations import RequirementRelation
from .constraint import RequirementDiagramConstraint


@injectable(as_type=RequirementDiagramConstraint, qualifier="requirement_members")
class RequirementContainsOnlyRequirementMembers(DiagramMembersConstraint, RequirementDiagramConstraint):
    element_types: ClassVar = (Requirement, RequirementElement)
    relation_types: ClassVar = (RequirementRelation,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a requirement diagram"
    relation_description: ClassVar[str] = "a requirement relation"
    annotation_description: ClassVar[str] = "valid in a requirement diagram"

    @property
    def code(self) -> str:
        return "requirement.member_type"
