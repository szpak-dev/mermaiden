
from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from .elements import Class
from .relations import ClassRelation


class ClassDiagramConstraint(Constraint):
    pass

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
