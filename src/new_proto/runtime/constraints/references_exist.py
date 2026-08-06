from dataclasses import dataclass

from wireup import injectable

from ...core.annotation import TargetKind
from ...core.constraint import Constraint, Violation
from ...core.diagram import Diagram


@injectable(as_type=Constraint, qualifier="references_exist")
@dataclass(frozen=True, slots=True)
class ReferencesExist(Constraint):
    @property
    def code(self) -> str:
        return "structure.references"

    def visit(self, diagram: Diagram) -> tuple[Violation, ...]:
        element_ids = {item.id for item in diagram.elements}
        relation_ids = {item.id for item in diagram.relations}
        issues: list[Violation] = []
        for relation in diagram.relations:
            for participant_id in relation.participant_ids:
                if participant_id not in element_ids:
                    issues.append(
                        self.violation(
                            f"Relation '{relation.id}' references unknown element '{participant_id}'.",
                            path=f"relations.{relation.id}",
                        )
                    )
        for element in diagram.elements:
            if element.owner_id is not None and element.owner_id not in element_ids:
                issues.append(
                    self.violation(
                        f"Element '{element.id}' references unknown owner '{element.owner_id}'.",
                        path=f"elements.{element.id}.owner_id",
                    )
                )
        for annotation in diagram.annotations:
            for target in annotation.targets:
                exists = (
                    (target.kind is TargetKind.DIAGRAM and target.id == diagram.id)
                    or (target.kind is TargetKind.ELEMENT and target.id in element_ids)
                    or (target.kind is TargetKind.RELATION and target.id in relation_ids)
                )
                if not exists:
                    issues.append(
                        self.violation(
                            f"Annotation '{annotation.id}' has unknown {target.kind} target '{target.id}'.",
                            path=f"annotations.{annotation.id}",
                        )
                    )
        return tuple(issues)
