from abc import ABC
from typing import ClassVar

from wireup import injectable

from ...core.constraint import Constraint, ConstraintDiagram, ConstraintLevel, Violation
from ..domain import DiagramMembersConstraint
from .elements import Requirement, RequirementElement
from .relations import RequirementRelation


class RequirementDiagramConstraint(Constraint, ABC):
    @staticmethod
    def relations(diagram: ConstraintDiagram) -> tuple[RequirementRelation, ...]:
        return tuple(item for item in diagram.find_relations() if isinstance(item, RequirementRelation))

@injectable(as_type=RequirementDiagramConstraint, qualifier="requirement_relations")
class RelationsAreValid(RequirementDiagramConstraint):
    @property
    def code(self) -> str:
        return "requirement.relation"

    @property
    def level(self) -> ConstraintLevel:
        return ConstraintLevel.BLOCKING

    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        elements = {item.id: item for item in diagram.walk_elements()}
        issues: list[Violation] = []
        for relation in self.relations(diagram):
            if len(relation.element_ids) != 2:
                issues.append(
                    self.violation(
                        f"Relation '{relation.id}' requires exactly one source and one target.",
                        path=f"relations.{relation.id}",
                    )
                )
                continue
            for endpoint in (relation.source_id, relation.target_id):
                if not isinstance(elements.get(endpoint), (Requirement, RequirementElement)):
                    issues.append(
                        self.violation(
                            f"Relation '{relation.id}' endpoint '{endpoint}' must be a requirement or element.",
                            path=f"relations.{relation.id}",
                        )
                    )
        return tuple(issues)

@injectable(as_type=RequirementDiagramConstraint, qualifier="requirement_members")
class RequirementContainsOnlyRequirementMembers(DiagramMembersConstraint, RequirementDiagramConstraint):
    element_types: ClassVar = (Requirement, RequirementElement)
    relation_types: ClassVar = (RequirementRelation,)
    annotation_types: ClassVar = ()
    element_description: ClassVar[str] = "valid in a requirement diagram"
    relation_description: ClassVar[str] = "a requirement relation"
    annotation_description: ClassVar[str] = "valid in a requirement diagram"

    @property
    def code(self) -> str:
        return "requirement.member_type"
