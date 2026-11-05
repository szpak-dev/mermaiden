from wireup import injectable

from ...core.domain import ConstraintDiagram, Violation
from ..domain import DiagramConstraint


@injectable(qualifier="sankey_structure")
class SankeyConstraint(DiagramConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        owners: dict[str, str] = {}
        issues: list[Violation] = []
        for node in diagram.walk_elements(""):
            if node.label in owners:
                issues.append(
                    self.violation(
                        f"Sankey node '{node.id}' shares label '{node.label}' with '{owners[node.label]}'. "
                        "Sankey labels must be unique.",
                        path=f"elements.{node.id}.label",
                    )
                )
            else:
                owners[node.label] = node.id
        return tuple(issues)
