from wireup import injectable

from ....core.constraint import ConstraintDiagram, ConstraintLevel, Violation
from ..elements import Requirement, RequirementElement
from .constraint import RequirementDiagramConstraint


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
