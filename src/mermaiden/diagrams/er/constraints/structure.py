from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from .constraint import EntityRelationshipDiagramConstraint


@injectable(as_type=EntityRelationshipDiagramConstraint, qualifier="er_structure")
class EntityRelationshipDiagramStructure(EntityRelationshipDiagramConstraint):
    @property
    def code(self) -> str:
        return "er.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        return ()
