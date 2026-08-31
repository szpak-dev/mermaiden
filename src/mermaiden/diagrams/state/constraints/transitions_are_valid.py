from wireup import injectable

from ....core.domain import ConstraintDiagram, Violation
from ..elements import StateEndpoint
from .domain import StateDiagramConstraint


@injectable(as_type=StateDiagramConstraint, qualifier="state_transitions")
class TransitionsAreValid(StateDiagramConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements("")}
        issues: list[Violation] = []
        for transition in self.transitions(diagram):
            if len(transition.element_ids) != 2:
                issues.append(
                    self.violation(
                        f"Transition '{transition.id}' requires exactly one source and one target.",
                        path=f"relations.{transition.id}",
                    )
                )
                continue
            for endpoint in (transition.source_id, transition.target_id):
                if not isinstance(elements.get(endpoint), StateEndpoint):
                    issues.append(
                        self.violation(
                            f"Transition '{transition.id}' endpoint '{endpoint}' must be a state node.",
                            path=f"relations.{transition.id}",
                        )
                    )
        return tuple(issues)
