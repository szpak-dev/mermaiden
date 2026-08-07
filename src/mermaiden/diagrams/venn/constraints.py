from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import DiagramMembersConstraint
from .elements import VennSet, VennText, VennUnion


class VennConstraint(Constraint, ABC):
    pass

@injectable(as_type=VennConstraint, qualifier="venn_members")
class VennMembers(DiagramMembersConstraint, VennConstraint):
    element_types: ClassVar = (VennSet, VennText, VennUnion)
    relation_types: ClassVar = ()
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a Venn diagram"
    relation_description: ClassVar[str] = "valid in a Venn diagram"
    annotation_description: ClassVar[str] = "valid in a Venn diagram"

    @property
    def code(self) -> str:
        return "venn.member_type"

@injectable(as_type=VennConstraint, qualifier="venn_structure")
class VennStructure(VennConstraint):
    @property
    def code(self) -> str:
        return "venn.structure"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

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
