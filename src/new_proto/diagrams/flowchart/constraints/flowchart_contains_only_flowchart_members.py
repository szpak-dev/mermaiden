from dataclasses import dataclass

from wireup import injectable

from ....core.constraint import Violation
from ....core.diagram import Diagram
from ..elements.elements import FlowGroup, FlowNode
from ..relations import Flow
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="flowchart_members")
@dataclass(frozen=True, slots=True)
class FlowchartContainsOnlyFlowchartMembers(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.member_type"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(f"Element '{item.id}' is not a flowchart element.", path=f"elements.{item.id}")
            for item in diagram.elements
            if not isinstance(item, FlowNode | FlowGroup)
        ]
        issues.extend(
            self.violation(f"Relation '{item.id}' is not a flow.", path=f"relations.{item.id}")
            for item in diagram.relations
            if not isinstance(item, Flow)
        )
        return tuple(issues)
