from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.relation import Relation
from ..domain import DiagramRelationMember


class ClassDiagramRelationMember(DiagramRelationMember):
    description: ClassVar[str] = "a class relation"


class ClassRelationKind(StrEnum):
    ASSOCIATION = "--"
    INHERITANCE = "<|--"
    COMPOSITION = "*--"
    AGGREGATION = "o--"
    DEPENDENCY = "<.."
    REALIZATION = "<|.."


@dataclass(frozen=True, slots=True)
class ClassRelation(Relation, ClassDiagramRelationMember):
    kind: ClassVar[str] = "class_relation"
    relation_kind: ClassRelationKind = ClassRelationKind.ASSOCIATION
    source_label: str = ""
    target_label: str = ""

    @property
    def source_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def target_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""
