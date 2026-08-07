from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import (
    DiagramAnnotationMember,
)


class EntityRelationshipDiagramConstraint(Constraint, ABC):
    pass

class EntityRelationshipAnnotationMember(DiagramAnnotationMember):
    description: ClassVar[str] = "valid in an ER diagram"


@injectable(as_type=EntityRelationshipDiagramConstraint, qualifier="er_structure")
class EntityRelationshipDiagramStructure(EntityRelationshipDiagramConstraint):
    @property
    def code(self) -> str:
        return "er.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
