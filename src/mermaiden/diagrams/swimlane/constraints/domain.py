from ....core.domain import ConstraintDiagram
from ...domain import DiagramConstraint
from ..relations import Flow


class SwimlaneConstraint(DiagramConstraint):
    def flows(self, diagram: ConstraintDiagram) -> tuple[Flow, ...]:
        return tuple(item for item in diagram.find_relations("") if isinstance(item, Flow))
