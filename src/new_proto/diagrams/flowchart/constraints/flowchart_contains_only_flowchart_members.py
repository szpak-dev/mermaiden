from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import ConstraintLevel, Violation
from ....core.diagram import Diagram
from ..annotations import Note
from ..elements import FlowGroup, FlowNode
from ..relations import Flow
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="flowchart_members")
@dataclass(frozen=True, slots=True)
class FlowchartContainsOnlyFlowchartMembers(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.member_type"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(f"Element '{item.id}' is not a flowchart element.", path=f"elements.{item.id}")
            for item in diagram.walk_elements()
            if not isinstance(item, FlowNode | FlowGroup)
        ]
        issues.extend(
            self.violation(f"Relation '{item.id}' is not a flow.", path=f"relations.{item.id}")
            for item in diagram.find_relations()
            if not isinstance(item, Flow)
        )
        issues.extend(
            self.violation(
                f"Annotation '{item.id}' is not a flowchart note.",
                path=f"annotations.{item.id}",
            )
            for item in diagram.find_annotations()
            if not isinstance(item, Note)
        )
        return tuple(issues)
