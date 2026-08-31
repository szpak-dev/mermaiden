from wireup import injectable

from ...core.domain import ConstraintDiagram, Violation
from ..domain import DiagramConstraint
from .elements import Domain
from .relations import Transition


class CynefinDiagramConstraint(DiagramConstraint):
    pass


@injectable(as_type=CynefinDiagramConstraint, qualifier="cynefin_structure")
class CynefinDiagramStructure(CynefinDiagramConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        domains = {item.id: item for item in diagram.walk_elements() if isinstance(item, Domain)}
        return tuple(
            self.violation(f"Cynefin transition '{item.id}' must cross distinct domains.", path=f"relations.{item.id}")
            for item in diagram.find_relations()
            if isinstance(item, Transition)
            if len(item.element_ids) == 2
            if (source := domains.get(item.element_ids[0])) is not None
            if (target := domains.get(item.element_ids[1])) is not None
            if source.domain is target.domain
        )
