from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import DiagramMembersConstraint
from .annotations import ClassNote
from .elements import Class, ClassNamespace
from .relations import ClassRelation


class ClassDiagramConstraint(Constraint):
    pass

@injectable(as_type=ClassDiagramConstraint, qualifier="classdiagram_members")
class ClassDiagramMembers(DiagramMembersConstraint, ClassDiagramConstraint):
    element_types: ClassVar = (Class, ClassNamespace)
    relation_types: ClassVar = (ClassRelation,)
    annotation_types: ClassVar = (ClassNote,)
    element_description: ClassVar[str] = "a class"
    relation_description: ClassVar[str] = "a class relation"
    annotation_description: ClassVar[str] = "a class note"

    @property
    def code(self) -> str:
        return "classdiagram.members"

@injectable(as_type=ClassDiagramConstraint, qualifier="classdiagram_relations")
class ClassRelationsAreBinary(ClassDiagramConstraint):
    @property
    def code(self) -> str:
        return "classdiagram.relations"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        classes = {item.id for item in diagram.walk_elements() if isinstance(item, Class)}
        return tuple(
            self.violation(f"Relation '{item.id}' must connect two classes.", path=f"relations.{item.id}")
            for item in diagram.find_relations()
            if isinstance(item, ClassRelation)
            and (len(item.element_ids) != 2 or not set(item.element_ids).issubset(classes))
        )
