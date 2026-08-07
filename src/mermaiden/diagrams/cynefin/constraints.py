from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import DiagramMembersConstraint
from .elements import Domain
from .relations import Transition


class CynefinDiagramConstraint(Constraint, ABC):
    pass

@injectable(as_type=CynefinDiagramConstraint, qualifier="cynefin_members")
class CynefinDiagramMembers(DiagramMembersConstraint, CynefinDiagramConstraint):
    element_types: ClassVar = (Domain,)
    relation_types: ClassVar = (Transition,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Cynefin diagram"
    relation_description: ClassVar[str] = "valid in Cynefin diagram"
    annotation_description: ClassVar[str] = "valid in Cynefin diagram"

    @property
    def code(self) -> str:
        return "cynefin.member_type"

@injectable(as_type=CynefinDiagramConstraint, qualifier="cynefin_structure")
class CynefinDiagramStructure(CynefinDiagramConstraint):
    @property
    def code(self) -> str:
        return "cynefin.structure"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        domains = {item.id: item for item in diagram.walk_elements() if isinstance(item, Domain)}
        return tuple(
            self.violation(
                f"Cynefin transition '{item.id}' must cross distinct domains.", path=f"relations.{item.id}"
            )
            for item in diagram.find_relations()
            if isinstance(item, Transition)
            if len(item.element_ids) == 2
            if (source := domains.get(item.element_ids[0])) is not None
            if (target := domains.get(item.element_ids[1])) is not None
            if source.domain is target.domain
        )
