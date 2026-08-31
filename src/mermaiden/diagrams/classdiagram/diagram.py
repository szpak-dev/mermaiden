from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.domain import ChangeReport
from ..domain import DiagramDefinition, DiagramModel
from .annotations import ClassNotes
from .configuration import ClassDiagramConfiguration
from .constraints import ClassDiagramConstraint
from .elements import Class, ClassAttribute, ClassMethod, ClassNamespace
from .relations import ClassRelation, ClassRelationKind


@injectable(as_type=DiagramModel, qualifier="classdiagram", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ClassDiagram(DiagramModel):
    constraints: Sequence[ClassDiagramConstraint]
    configuration: ClassDiagramConfiguration = field(default_factory=ClassDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "classDiagram",
        "Class diagram",
        "class",
        "ClassDiagramConfig",
    )

    def add_class(
        self,
        id: str,
        label: str,
        *,
        attributes: Sequence[str | ClassAttribute] = (),
        methods: Sequence[str | ClassMethod] = (),
        annotations: Sequence[str] = (),
        comment: str = "",
        parent_id: str = "",
    ) -> ChangeReport:
        return self._add_element(
            f"add class '{id}'",
            Class(
                id=id,
                label=label,
                attributes=tuple(attributes),
                methods=tuple(methods),
                annotations=tuple(annotations),
                comment=comment,
            ),
            parent_id,
        )

    def add_namespace(self, id: str, label: str = "", *, comment: str = "") -> ChangeReport:
        return self._add_element(
            f"add namespace '{id}'", ClassNamespace(id=id, label=label or id, elements=(), comment=comment)
        )

    def add_relation(
        self,
        id: str,
        source_id: str,
        target_id: str,
        relation_kind: ClassRelationKind = ClassRelationKind.ASSOCIATION,
        label: str = "",
        source_label: str = "",
        target_label: str = "",
    ) -> ChangeReport:
        return self._add_relation(
            f"add class relation '{id}'",
            ClassRelation(
                id=id,
                element_ids=(source_id, target_id),
                label=label,
                relation_kind=relation_kind,
                source_label=source_label,
                target_label=target_label,
            ),
        )

    def add_note(self, id: str, class_id: str, text: str) -> ChangeReport:
        return self._annotate(f"add class note '{id}'", ClassNotes(), id, {"text": text}, (class_id,))
