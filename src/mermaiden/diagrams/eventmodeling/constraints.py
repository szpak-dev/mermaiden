
from wireup import injectable

from ...core.constraint import ConstraintDiagram, Violation
from ..domain import DiagramConstraint
from .elements import Swimlane, SwimlaneMember
from .relations import Flow


class EventModelingDiagramConstraint(DiagramConstraint):
    pass


@injectable(as_type=EventModelingDiagramConstraint, qualifier="eventmodeling_structure")
class EventModelingDiagramStructure(EventModelingDiagramConstraint):

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(
                f"Event Modeling element '{item.id}' should belong to a swimlane.", path=f"elements.{item.id}"
            )
            for item in diagram.root_elements
            if isinstance(item, SwimlaneMember)
        ]
        issues.extend(
            self.violation(f"Event Modeling flow '{item.id}' cannot be self-referential.", path=f"relations.{item.id}")
            for item in diagram.find_relations()
            if isinstance(item, Flow) and len(item.element_ids) == 2 and item.element_ids[0] == item.element_ids[1]
        )
        issues.extend(
            self.violation(f"Event Modeling swimlane '{item.id}' must have a label.", path=f"elements.{item.id}")
            for item in diagram.root_elements
            if isinstance(item, Swimlane) and not item.label
        )
        return tuple(issues)
