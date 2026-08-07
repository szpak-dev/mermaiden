from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..base import DiagramModel
from .annotations import ClassNotes
from .constraints import ClassDiagramConstraint
from .elements import Class, ClassAttribute, ClassMethod, ClassNamespace
from .relations import ClassRelation, ClassRelationKind


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ClassDiagram(DiagramModel):
    constraints: Sequence[ClassDiagramConstraint]
    syntax: ClassVar[str] = "classDiagram"

    def add_class(
        self,
        id: str,
        label: str = "",
        *,
        attributes: Sequence[str | ClassAttribute] = (),
        methods: Sequence[str | ClassMethod] = (),
        annotations: Sequence[str] = (),
        comment: str = "",
        parent_id: str = "",
    ) -> ChangeReport:
        return self._add_element(
            f"add class '{id}'",
            Class(id, label or id, tuple(attributes), tuple(methods), tuple(annotations), comment),
            parent_id,
        )

    def add_namespace(self, id: str, label: str = "", *, comment: str = "") -> ChangeReport:
        return self._add_element(f"add namespace '{id}'", ClassNamespace(id, label or id, (), comment))

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
            ClassRelation(id, (source_id, target_id), label, relation_kind, source_label, target_label),
        )

    def add_note(self, id: str, class_id: str, text: str) -> ChangeReport:
        return self._annotate(f"add class note '{id}'", ClassNotes(), id, {"text": text}, (class_id,))
