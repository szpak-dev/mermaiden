from wireup import injectable

from ...core.domain import Constraint, ConstraintDiagram, TargetKind, Violation
from ..domain import StructureConstraint


@injectable(as_type=Constraint, qualifier="references_exist")
class ReferencesExist(StructureConstraint):
    def visit(self, diagram: ConstraintDiagram) -> tuple[Violation, ...]:
        element_ids = {item.id for item in diagram.walk_elements()}
        relation_ids = {item.id for item in diagram.find_relations()}
        issues: list[Violation] = []
        for relation in diagram.find_relations():
            for element_id in relation.element_ids:
                if element_id not in element_ids:
                    issues.append(
                        self.violation(
                            f"Relation '{relation.id}' references unknown element '{element_id}'.",
                            path=f"relations.{relation.id}",
                        )
                    )
        for annotation in diagram.find_annotations():
            for target in annotation.targets:
                exists = (target.kind is TargetKind.ELEMENT and target.id in element_ids) or (
                    target.kind is TargetKind.RELATION and target.id in relation_ids
                )
                if not exists:
                    issues.append(
                        self.violation(
                            f"Annotation '{annotation.id}' references unknown target '{target.id}'.",
                            path=f"annotations.{annotation.id}",
                        )
                    )
        return tuple(issues)
