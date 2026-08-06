from dataclasses import dataclass

from ...core.annotation import Annotation
from ...core.constraint import Constraint
from ...core.element import Element
from ...core.relation import Relation


@dataclass(frozen=True, slots=True)
class DiagramDraft:
    id: str
    elements: tuple[Element, ...] = ()
    relations: tuple[Relation, ...] = ()
    annotations: tuple[Annotation, ...] = ()
    constraints: tuple[Constraint, ...] = ()
