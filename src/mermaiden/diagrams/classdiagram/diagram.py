from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.characters import OptionalIdentifier
from ...core.domain import ChangeReport, Container, Element
from ..domain import (
    CommandDefault,
    DiagramCommandFeature,
    DiagramDefinition,
    DiagramFeature,
    DiagramModel,
)
from .configuration import ClassDiagramConfiguration
from .constraints import ClassDiagramConstraint
from .elements import Class, ClassNamespace
from .relations import ClassRelation, ClassRelationKind
from .values.members import ClassAttribute, ClassMethod
from .values.text import ClassIdentifier, ClassText, MemberName, OptionalClassText


@injectable(as_type=DiagramModel, qualifier="classdiagram", lifetime="transient")
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

    feature: ClassVar[DiagramFeature] = DiagramFeature(
        configuration=ClassDiagramConfiguration,
        elements=(Class, ClassNamespace),
        relations=(ClassRelation,),
        commands=(
            DiagramCommandFeature(
                "add_class",
                {
                    "id": ClassIdentifier,
                    "label": ClassText,
                    "attributes": CommandDefault(Sequence[ClassAttribute], ()),
                    "methods": CommandDefault(Sequence[ClassMethod], ()),
                    "annotations": CommandDefault(Sequence[MemberName], ()),
                    "comment": CommandDefault(OptionalClassText, ""),
                    "parent_id": CommandDefault(OptionalIdentifier, ""),
                },
            ),
            DiagramCommandFeature(
                "add_namespace",
                {
                    "id": ClassIdentifier,
                    "label": CommandDefault(OptionalClassText, ""),
                    "comment": CommandDefault(OptionalClassText, ""),
                },
            ),
            DiagramCommandFeature(
                "add_relation",
                {
                    "id": ClassIdentifier,
                    "source_id": ClassIdentifier,
                    "target_id": ClassIdentifier,
                    "relation_kind": CommandDefault(ClassRelationKind, ClassRelationKind.ASSOCIATION),
                    "label": CommandDefault(OptionalClassText, ""),
                    "source_label": CommandDefault(OptionalClassText, ""),
                    "target_label": CommandDefault(OptionalClassText, ""),
                },
            ),
        ),
    )

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {**super(ClassDiagram, self).mermaid_configuration, "htmlLabels": False}

    def accepts_parent(self, element_type: type[Element], parent_type: type[Container] | None) -> bool:
        if element_type is ClassNamespace:
            return parent_type is None
        return element_type is Class and (parent_type is None or parent_type is ClassNamespace)

    def add_class(
        self,
        id: str,
        label: str,
        *,
        attributes: Sequence[ClassAttribute] = (),
        methods: Sequence[ClassMethod] = (),
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
