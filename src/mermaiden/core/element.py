from abc import ABC

from .model import ClassifiedValueModel


class Element(ClassifiedValueModel, ABC):
    id: str
    label: str


class Entity(Element):
    pass


class RequiresChildren:
    pass


class Container(Element):
    elements: tuple[Element, ...] = ()
