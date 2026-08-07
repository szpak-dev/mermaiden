from abc import ABC

from ....core.constraint import Constraint, ConstraintDiagram
from ..relations import Flow


class SwimlaneConstraint(Constraint, ABC):
    @staticmethod
    def flows(diagram: ConstraintDiagram) -> tuple[Flow, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, Flow))
