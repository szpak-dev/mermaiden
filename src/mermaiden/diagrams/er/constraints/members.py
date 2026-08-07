from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..elements import Entity, EntityAttribute
from ..relations import EntityRelationship
from .constraint import EntityRelationshipDiagramConstraint


@injectable(as_type=EntityRelationshipDiagramConstraint, qualifier="er_members")
class EntityRelationshipDiagramMembers(DiagramMembersConstraint, EntityRelationshipDiagramConstraint):
    element_types: ClassVar = (Entity, EntityAttribute)
    relation_types: ClassVar = (EntityRelationship,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in an ER diagram"
    relation_description: ClassVar[str] = "valid in an ER diagram"
    annotation_description: ClassVar[str] = "valid in an ER diagram"

    @property
    def code(self) -> str:
        return "er.member_type"
