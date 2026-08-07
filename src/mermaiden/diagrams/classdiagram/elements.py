from enum import StrEnum

from ...core.element import Container, Entity
from ...core.model import ValueModel


class Visibility(StrEnum):
    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"
    PACKAGE = "~"


class ClassAttribute(ValueModel):

    name: str
    type: str = ""
    visibility: Visibility = Visibility.PUBLIC

    def __str__(self) -> str:
        return f"{self.visibility}{self.type} {self.name}".strip()


class ClassMethod(ValueModel):

    name: str
    parameters: tuple[str, ...] = ()
    return_type: str = ""
    visibility: Visibility = Visibility.PUBLIC

    def __str__(self) -> str:
        result = f"{self.visibility}{self.name}({', '.join(self.parameters)})"
        return f"{result} {self.return_type}" if self.return_type else result


class Class(Entity):
    attributes: tuple[str | ClassAttribute, ...] = ()
    methods: tuple[str | ClassMethod, ...] = ()
    annotations: tuple[str, ...] = ()
    comment: str = ""


class ClassNamespace(Container):
    comment: str = ""
