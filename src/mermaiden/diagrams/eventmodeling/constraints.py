from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import Actor, Command, Event, Swimlane, View
from .relations import Flow


class EventModelingDiagramConstraint(Constraint, ABC):
    pass

@injectable(as_type=EventModelingDiagramConstraint, qualifier="eventmodeling_members")
class EventModelingDiagramMembers(DiagramMembersConstraint, EventModelingDiagramConstraint):
    element_types: ClassVar = (Event, Command, View, Actor, Swimlane,)
    relation_types: ClassVar = (Flow,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Event Modeling diagram"
    relation_description: ClassVar[str] = "valid in Event Modeling diagram"
    annotation_description: ClassVar[str] = "valid in Event Modeling diagram"

    @property
    def code(self) -> str:
        return "eventmodeling.member_type"

@injectable(as_type=EventModelingDiagramConstraint, qualifier="eventmodeling_structure")
class EventModelingDiagramStructure(EventModelingDiagramConstraint):
    @property
    def code(self) -> str:
        return "eventmodeling.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(
                f"Event Modeling element '{item.id}' should belong to a swimlane.", path=f"elements.{item.id}"
            )
            for item in diagram.root_elements
            if isinstance(item, (Actor, Command, Event, View))
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
