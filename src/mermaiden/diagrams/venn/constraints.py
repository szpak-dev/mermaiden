
from wireup import injectable

from ...core.constraint import BlockingConstraint, ConstraintDiagram, Violation
from .elements import VennSet, VennUnion


class VennConstraint(BlockingConstraint):
    pass



@injectable(as_type=VennConstraint, qualifier="venn_structure")
class VennStructure(VennConstraint):
    @property
    def code(self) -> str:
        return "venn.structure"


    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        known_sets = {item.id for item in diagram.walk_elements() if isinstance(item, VennSet)}
        return tuple(
            self.violation(
                f"Venn union '{item.id}' references undefined sets: {', '.join(missing)}.",
                path=f"elements.{item.id}",
            )
            for item in diagram.root_elements
            if isinstance(item, VennUnion)
            if (missing := tuple(set(item.set_ids).difference(known_sets)))
        )
