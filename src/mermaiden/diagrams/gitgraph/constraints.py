
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation
from .elements import Branch, Checkout, Commit


class GitGraphDiagramConstraint(BlockingConstraint):
    pass


@injectable(as_type=GitGraphDiagramConstraint, qualifier="gitgraph_structure")
class GitGraphDiagramStructure(GitGraphDiagramConstraint):
    @property
    def code(self) -> str:
        return "gitgraph.structure"


    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        branches = tuple(item for item in diagram.root_elements if isinstance(item, Branch))
        branch_names = {item.label for item in branches}
        issues = [
            self.violation(f"Git branch '{item.id}' must have a non-empty identifier.", path=f"elements.{item.id}")
            for item in branches
            if not item.label or not item.label.replace("_", "").replace("-", "").isalnum()
        ]
        issues.extend(
            self.violation(f"Git branch '{item.id}' must use a non-negative order.", path=f"elements.{item.id}")
            for item in branches
            if item.order is not None and item.order < 0
        )
        issues.extend(
            self.violation(
                f"Checkout '{item.id}' references unknown branch '{item.label}'.",
                path=f"elements.{item.id}",
            )
            for item in diagram.root_elements
            if isinstance(item, Checkout) and item.label not in {"main", *branch_names}
        )
        issues.extend(
            self.violation(
                f"Commit '{item.id}' has unsupported type '{item.commit_type}'.",
                path=f"elements.{item.id}",
            )
            for item in diagram.root_elements
            if isinstance(item, Commit)
            if item.commit_type and item.commit_type not in {"NORMAL", "REVERSE", "HIGHLIGHT"}
        )
        return tuple(issues)
