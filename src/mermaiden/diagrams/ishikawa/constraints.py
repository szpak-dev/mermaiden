from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, Violation
from ..domain import DiagramMembersConstraint
from .elements import Category, Cause, Effect
from .relations import CauseRelation


class IshikawaDiagramConstraint(Constraint, ABC):
    pass

@injectable(as_type=IshikawaDiagramConstraint, qualifier="ishikawa_members")
class IshikawaDiagramMembers(DiagramMembersConstraint, IshikawaDiagramConstraint):
    element_types: ClassVar = (Effect, Cause, Category,)
    relation_types: ClassVar = (CauseRelation,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in Ishikawa diagram"
    relation_description: ClassVar[str] = "valid in Ishikawa diagram"
    annotation_description: ClassVar[str] = "valid in Ishikawa diagram"

    @property
    def code(self) -> str:
        return "ishikawa.member_type"

@injectable(as_type=IshikawaDiagramConstraint, qualifier="ishikawa_structure")
class IshikawaDiagramStructure(IshikawaDiagramConstraint):
    @property
    def code(self) -> str:
        return "ishikawa.structure"

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        effects = tuple(item for item in diagram.root_elements if isinstance(item, Effect))
        issues = [
            self.violation("Ishikawa diagrams should define exactly one effect.", path="elements")
            for _ in [None]
            if len(effects) != 1
        ]
        issues.extend(
            self.violation(f"Ishikawa cause '{item.id}' should belong to a category.", path=f"elements.{item.id}")
            for item in diagram.root_elements
            if isinstance(item, Cause)
        )
        issues.extend(
            self.violation(f"Ishikawa category '{item.id}' must have a label.", path=f"elements.{item.id}")
            for item in diagram.root_elements
            if isinstance(item, Category) and not item.label
        )
        return tuple(issues)
