from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, Violation
from ...core.diagram import Diagram
from ...core.element import Container


@injectable(as_type=Constraint, qualifier="ownership_is_valid")
@dataclass(frozen=True, slots=True)
class OwnershipIsValid(Constraint):
    @property
    def code(self) -> str:
        return "structure.ownership"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.elements}
        issues: list[Violation] = []
        for element in diagram.elements:
            if (
                element.owner_id is not None
                and element.owner_id in elements
                and not isinstance(elements[element.owner_id], Container)
            ):
                issues.append(
                    self.violation(
                        f"Owner '{element.owner_id}' is not a container.",
                        path=f"elements.{element.id}.owner_id",
                    )
                )
            chain: set[str] = set()
            current = element
            while current.owner_id is not None and current.owner_id in elements:
                if current.owner_id == element.id or current.owner_id in chain:
                    issues.append(
                        self.violation(
                            f"Ownership cycle includes element '{element.id}'.",
                            path=f"elements.{element.id}.owner_id",
                        )
                    )
                    break
                chain.add(current.owner_id)
                current = elements[current.owner_id]
        return tuple(issues)
