
from wireup import injectable

from ..domain import DiagramConstraint


@injectable(qualifier="er_structure")
class EntityRelationshipDiagramConstraint(DiagramConstraint):
    pass
