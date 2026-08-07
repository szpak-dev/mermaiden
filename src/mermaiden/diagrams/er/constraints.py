from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import Entity, EntityAttribute
from .relations import EntityRelationship


class EntityRelationshipDiagramConstraint(Constraint, ABC):
    pass

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

@injectable(as_type=EntityRelationshipDiagramConstraint, qualifier="er_structure")
class EntityRelationshipDiagramStructure(EntityRelationshipDiagramConstraint):
    @property
    def code(self) -> str:
        return "er.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
