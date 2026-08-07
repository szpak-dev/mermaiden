from wireup import injectable

from ....core.constraint import ConstraintDiagram, Violation
from ..elements import Decision
from ..relations import ConditionalFlow
from .constraint import FlowchartConstraint


@injectable(as_type=FlowchartConstraint, qualifier="decision_branches_are_conditioned")
class DecisionBranchesAreConditioned(FlowchartConstraint):
    @property
    def code(self) -> str:
        return "flowchart.decision_conditions"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        issues: list[Violation] = []
        flows = self.flows(diagram)
        for decision in (item for item in diagram.walk_elements() if isinstance(item, Decision)):
            branches = tuple(flow for flow in flows if flow.source_id == decision.id)
            conditions = [flow.condition.strip() for flow in branches if isinstance(flow, ConditionalFlow)]
            if len(conditions) != len(branches) or any(not item for item in conditions):
                issues.append(
                    self.violation(
                        f"Every branch from decision '{decision.id}' needs a condition.",
                        path=f"elements.{decision.id}",
                    )
                )
            elif len(set(conditions)) != len(conditions):
                issues.append(
                    self.violation(
                        f"Decision '{decision.id}' has duplicate conditions.",
                        path=f"elements.{decision.id}",
                    )
                )
        return tuple(issues)
