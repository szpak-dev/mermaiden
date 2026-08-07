from dataclasses import dataclass

from wireup import injectable

from ...core.constraint import Constraint, ConstraintLevel, Violation
from ...core.diagram import Diagram
from .annotations import ClassNote
from .elements import Class, ClassNamespace
from .relations import ClassRelation


class ClassDiagramConstraint(Constraint):
    pass


@injectable(as_type=ClassDiagramConstraint, qualifier="classdiagram_members")
@dataclass(frozen=True, slots=True)
class ClassDiagramMembers(ClassDiagramConstraint):
    @property
    def code(self) -> str:
        return "classdiagram.members"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        issues = [
            self.violation(f"Element '{item.id}' is not a class.", path=f"elements.{item.id}")
            for item in diagram.walk_elements()
            if not isinstance(item, Class | ClassNamespace)
        ]
        issues.extend(
            self.violation(f"Relation '{item.id}' is not a class relation.", path=f"relations.{item.id}")
            for item in diagram.find_relations()
            if not isinstance(item, ClassRelation)
        )
        issues.extend(
            self.violation(f"Annotation '{item.id}' is not a class note.", path=f"annotations.{item.id}")
            for item in diagram.find_annotations()
            if not isinstance(item, ClassNote)
        )
        return tuple(issues)


@injectable(as_type=ClassDiagramConstraint, qualifier="classdiagram_relations")
@dataclass(frozen=True, slots=True)
class ClassRelationsAreBinary(ClassDiagramConstraint):
    @property
    def code(self) -> str:
        return "classdiagram.relations"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        classes = {item.id for item in diagram.walk_elements() if isinstance(item, Class)}
        return tuple(
            self.violation(f"Relation '{item.id}' must connect two classes.", path=f"relations.{item.id}")
            for item in diagram.find_relations()
            if isinstance(item, ClassRelation)
            and (len(item.element_ids) != 2 or not set(item.element_ids).issubset(classes))
        )
