from abc import ABC

from ....core.constraint import Constraint, ConstraintDiagram
from ..relations import RequirementRelation


class RequirementDiagramConstraint(Constraint, ABC):
    @staticmethod
    def relations(diagram: ConstraintDiagram) -> tuple[RequirementRelation, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, RequirementRelation))
