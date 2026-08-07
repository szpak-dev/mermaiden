from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from ...core.element import Container, Entity
from ..domain import DiagramElementMember


class ClassDiagramElementMember(DiagramElementMember):
    description: ClassVar[str] = "a class"


class Visibility(StrEnum):
    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"
    PACKAGE = "~"


@dataclass(frozen=True, slots=True)
class ClassAttribute:
    name: str
    type: str = ""
    visibility: Visibility = Visibility.PUBLIC

    def __str__(self) -> str:
        return f"{self.visibility}{self.type} {self.name}".strip()


@dataclass(frozen=True, slots=True)
class ClassMethod:
    name: str
    parameters: tuple[str, ...] = ()
    return_type: str = ""
    visibility: Visibility = Visibility.PUBLIC

    def __str__(self) -> str:
        result = f"{self.visibility}{self.name}({', '.join(self.parameters)})"
        return f"{result} {self.return_type}" if self.return_type else result


@dataclass(frozen=True, slots=True)
class Class(Entity, ClassDiagramElementMember):
    kind: ClassVar[str] = "class"
    attributes: tuple[str | ClassAttribute, ...] = ()
    methods: tuple[str | ClassMethod, ...] = ()
    annotations: tuple[str, ...] = ()
    comment: str = ""


@dataclass(frozen=True, slots=True)
class ClassNamespace(Container, ClassDiagramElementMember):
    kind: ClassVar[str] = "class_namespace"
    comment: str = ""
